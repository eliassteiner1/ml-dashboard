### IMPORTS ############################################################################################################
# standard library imports
import os
import sys
import threading
import time
from   collections import deque
from   typing import Any
import copy
from dataclasses import fields

# third-party library imports
import numpy as np
import torch
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from   plotly.subplots import make_subplots
import plotly.io as pio
from   torchinfo import summary
import webbrowser

# local library imports
from mldashboard.containers.datastore import Store, GraphStore, TraceData
from mldashboard.containers.setupconfig import Config, GraphConfig, TraceConfig

from .dash.dashapp import make_plotter_app
from .containers.datastore import Store, GraphStore

### DEFINITIONS ########################################################################################################

# TODO big, trace number starts at 0 right now, but graph is 1-3, probably change graphs to 0-2 !!

class DashPlotter:
    
    def __init__(self, CONFIG: Config, model: torch.nn = None, input_data: Any = None) -> None:

        # stores all the initial configuration parameters
        self._CONFIG = CONFIG
        self._CONFIG.sanitize()
        
        # stores all the raw data from the training loop (losses, etc...)
        self._store = self._make_store()
        
        # add a model summarry if available TODO: check if this still works, better alternatives? rework in general
        if (model is not None) and (input_data is not None):
            model_summary = summary(
                model, 
                input_data = input_data,
                col_names  = ["num_params"],
                col_width  = 12, # TODO: make more adjustable from CONFIG
                verbose    = False,
            )
            self._store.msummary = str(model_summary) # otherwise it's the default field string value
        
        # this is the container for the actual plotter app
        self._app = make_plotter_app(self._CONFIG, self._store)

    def _make_store(self) -> Store:
        
        # initialize with just the default fields, mostly sufficient
        store = Store()
        
        # need to fill the graph1-3 fields with a variable amount of trace-level containers 
        for fd in fields(Config):
            if fd.type is not GraphConfig:
                continue
            # need handles to the actual, graph-level container objects, not just the field name
            G_CFG: GraphConfig  = getattr(self._CONFIG, fd.name)
            g_store: GraphStore = getattr(store, fd.name)
    
            # iterate through all the traces that were configured for this graph and add elements for each
            for trace_cfg in G_CFG.traces:
                
                new_trace_data = TraceData()
                # if one traces graph's data is downsampled, all it's trace need the downsampled-x vector
                if G_CFG.nxdown is not False:
                    new_trace_data.add_xdown(totalx=G_CFG.totalx, nxdown=G_CFG.nxdown)
                # if one trace has errorbands, initialize the respective containers
                if trace_cfg.errors is True:
                    new_trace_data.add_errorband()
                
                # finally, FOR EACH trace in config, add a data-, t2id- and a2id-container, all on the same index! 
                g_store.add_trc_data(new_trace_data)
                g_store.add_trc_t2id() 
                g_store.add_trc_a2id()            
  
        return store

    def add_data(self, graph_nr: int, trace_nr: int, x: float, y: float, yStdLo: float = None, yStdHi: float = None):
        # TODO do robust sanitizing of input data! (like detach, cpu, remove Nans, etc...)

        if isinstance(y, torch.Tensor):
            y = y.detach().cpu().numpy()
        if isinstance(yStdLo, torch.Tensor):
            yStdLo = yStdLo.detach().cpu().numpy()
        if isinstance(yStdHi, torch.Tensor):
            yStdHi = yStdHi.detach().cpu().numpy()
        
        g_store: GraphStore = getattr(self._store, f"graph{graph_nr}")

        # add the standard raw data   
        g_store.trc_data[trace_nr].x.append(float(x))
        g_store.trc_data[trace_nr].y.append(float(y)) 
        
        # add error band data if neccessary
        if (yStdLo is not None) and ( yStdHi is not None):
            g_store.trc_data[trace_nr].ylo.append(float(y-yStdLo))
            g_store.trc_data[trace_nr].yhi.append(float(y+yStdHi)) 
        
        # track the running max / min to avoid taking min / max over all data
        if y < g_store.trc_data[trace_nr].ymin:
            g_store.trc_data[trace_nr].ymin    = float(y)
            g_store.trc_data[trace_nr].ynewmin = True
        if y > g_store.trc_data[trace_nr].ymax:
            g_store.trc_data[trace_nr].ymax    = float(y)
            g_store.trc_data[trace_nr].ynewmax = True

    def batchtimer(self, action: str, batch_size: int = None):
        # TODO: change to new containers!
        
        if action not in ["start", "stop", "read"]: # TODO: Enum
            raise ValueError(f"only 'start', 'stop' and 'read' allowed as action! (got {action})")
        
        if action == "start": # starts the timer
            self._store.procs.t0 = time.perf_counter()
            self._store.procs.t1 = None
        
        if action == "stop": # stops the timer and adds the recorded time as proc speed to store
            self._store.procs.t1 = time.perf_counter()
            if self._store.procs.t0 is None:
                raise ValueError("start time for batchtimer was not set!")
            if self._store.procs.t0 >= self._store.procs.t1:
                raise ValueError(f"got t0: {self._store.procs.t0} and t1: {self._store.procs.t1}!")
            if batch_size is None:
                raise ValueError(f"please specify a batch size when stopping the timer!")
            
            self._store.procs.speed.append(batch_size / (self._store.procs.t1 - self._store.procs.t0))
            self._store.procs.t0 = None
            self._store.procs.t1 = None
        
        if action == "read":
            if len(self._store.procs.speed) == 0:
                print("warning: there have been no processing speed timings yet!")
                return 0
            else:
                return sum(self._store.procs.speed) / len(self._store.procs.speed)
    

    
    
    def run_jupyter(self, host: str = "127.0.0.1", port: int = 8050):
        """For running the plotter in a Jupyter notebook. Handles all the threading and keeping alive automatically."""
        
        self._app.run(
            host         = host, 
            jupyter_mode = "tab", # also has "inline" ... 
            port         = port, 
            debug        = True, 
            use_reloader = False # this is necessary, because hot reload is not possible in daemon thread 
            )
        
    def run_script(self, host: str = "127.0.0.1", port: int = 8050):
        """For running the plotter in a script. Uses a daemon thread to avoid the app from blocking the script. Use run_script_spin a the end of the script to keep the app thread alive and be able to interact with data."""
        
        def _run():   
            self._app.run(
                host         = host,
                port         = port,     
                debug        = True,    
                use_reloader = False # this is necessary, because hot reload is not possible in daemon thread 
            )
        threading.Thread(target = _run, daemon = True).start()
        webbrowser.open_new_tab(f"http://{host}:{port}/")
        
    def run_script_spin(self):
        """For running the plotter in a script. Run this at the very end of the script. Keeps the app thread alive until the script is interrupted with ctrl+C to be able to view the data and interact with it."""
        
        print("Plotter dash app continues to run in the background. Press ctrl+C to stop.")
        try:
            while True:
                time.sleep(1) # lower cpu load!
        except KeyboardInterrupt:
            print("Terminating plotter dash app ...")

