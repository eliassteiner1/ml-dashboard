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
from mldashboard.containers.datastore import GraphStore
from mldashboard.containers.setupconfig import SetupConfig, GraphConfig, TraceConfig
from mldashboard.containers.datastore import DataStore, TraceStore

from mldashboard.dash import make_plotter_app


### DEFINITIONS ########################################################################################################

class DashPlotter:
    
    def __init__(self, CONFIG: SetupConfig, model: torch.nn = None, input_data: Any = None) -> None:

        self._CONFIG = CONFIG
        self._CONFIG.sanitize()
        
        # stores all the raw data from the training loop (losses, etc...)
        self._store = self._make_store()
        
        # add a model summarry if available TODO: check if this still works, better alternatives?
        if (model is not None) and (input_data is not None):
            model_summary = summary(
                model, 
                input_data = input_data,
                col_names  = ["num_params"],
                col_width  = 12, # TODO: make more adjustable from CONFIG
                verbose    = False,
            )
            self._store.msummary = str(model_summary) # otherwise it's the default field string value
        
        
        #XXX <-------------------------------------------------------------------------------------------
        
        # links an unique identifier to the respective trace number for each trace
        self._n2t = { 
            "g1": {},
            "g2": {},
            "g3": {},
        }
        
        # TODO: add an n2a dict for doing the same with annotations!
        ...
        
        # this is the container for the actual plotter app
        self._app = make_plotter_app(self._CONFIG, self._store, self._n2t)

    def _make_store(self) -> DataStore:
        
        # initialize with just the default fields, mostly sufficient
        store = DataStore()
        
        # iterate through all the attributes of datastore and modify only the "graphX" fields to add the traces
        for fd in fields(DataStore):
        
            if isinstance(fd.type, GraphStore):
                graph_config = getattr(self._CONFIG, fd.name)
                
                # iterate through all the traces that were configured for this graph, to add them to store
                for tr in graph_config.traces:
                    new_trace = TraceStore()
                    # add the downsampled-x axis array to the store for all the traces of this graph
                    if isinstance(graph_config.nxdown, int):
                        new_trace.add_xdown(totalx=graph_config.totalx, nxdown=graph_config.nxdown)
                    if tr.errors is True:
                        new_trace.add_errorband()  
                    # finally add the customized trace container to this graph
                    getattr(store, fd.name).traces += [new_trace]
                    
            # skip the other non-graph storages   
            else:
                continue
            
        return store

     
     
     
     
        
    def add_data(self, graph: int, trace: int, x: float, y: float, yStdLo: float = None, yStdHi: float = None):
        # TODO do robust sanitizing of input data! (like detach, cpu, remove Nans, etc...)
        
        # TODO: change to new containers!
        if isinstance(y, torch.Tensor):
            y = y.detach().cpu().numpy()
        if isinstance(yStdLo, torch.Tensor):
            yStdLo = yStdLo.detach().cpu().numpy()
        if isinstance(yStdHi, torch.Tensor):
            yStdHi = yStdHi.detach().cpu().numpy()
        
        # add the standard raw data   
        self._store[f"g{graph}"][f"t{trace}_x"].append(float(x))
        self._store[f"g{graph}"][f"t{trace}_y"].append(float(y)) 
        
        # add error band data if neccessary
        if (yStdLo is not None) and ( yStdHi is not None):
            self._store[f"g{graph}"][f"t{trace}_yLo"].append(float(y-yStdLo))
            self._store[f"g{graph}"][f"t{trace}_yHi"].append(float(y+yStdHi))
        
        # track the running max / min to avoid taking min / max over all data
        if y < self._store[f"g{graph}"][f"t{trace}_yMin"]:
            self._store[f"g{graph}"][f"t{trace}_yMin"]    = float(y)
            self._store[f"g{graph}"][f"t{trace}_yMinNew"] = True
        if y > self._store[f"g{graph}"][f"t{trace}_yMax"]:
            self._store[f"g{graph}"][f"t{trace}_yMax"]    = float(y)
            self._store[f"g{graph}"][f"t{trace}_yMaxNew"] = True




    def batchtimer(self, action: str, batch_size: int = None):
        # TODO: change to new containers!
        
        if action not in ["start", "stop", "read"]:
            raise ValueError(f"only 'start', 'stop' and 'read' allowed as action! (got {action})")
        
        if action == "start": # starts the timer
            self._store["proc"]["t0"] = time.perf_counter()
            self._store["proc"]["t1"] = None
        
        if action == "stop": # stops the timer and adds the recorded time as proc speed to store
            self._store["proc"]["t1"] = time.perf_counter()
            if self._store["proc"]["t0"] is None:
                raise ValueError("start time for batchtimer was not set!")
            if self._store["proc"]["t0"] >= self._store["proc"]["t1"]:
                raise ValueError(f"got t0: {self._store["proc"]["t0"]} and t1: {self._store["proc"]["t1"]}!")
            if batch_size is None:
                raise ValueError(f"please specify a batch size when stopping the timer!")
            
            self._store["proc"]["speed"].append(batch_size / (self._store["proc"]["t1"] - self._store["proc"]["t0"]))
            self._store["proc"]["t0"] = None
            self._store["proc"]["t1"] = None
        
        if action == "read":
            if len(self._store["proc"]["speed"]) == 0:
                print("warning: there have been no processing speed timings yet!")
                return 0
            else:
                return sum(self._store["proc"]["speed"]) / len(self._store["proc"]["speed"])
        
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

