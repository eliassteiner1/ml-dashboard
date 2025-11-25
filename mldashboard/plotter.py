### IMPORTS ############################################################################################################
# standard library imports
import os
import sys
import threading
import time
from   collections import deque
from   typing import Any
import copy
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
from   mldashboard.dash import make_plotter_app

### DEFINITIONS ########################################################################################################

class DashPlotter:
    
    def __init__(self, setup_options: dict, model: torch.nn = None, input_data: Any = None):
        
         # TODO: sanitize input options
        self._setup_options = setup_options
        # determine if any trace of a graph needs it to be a plotly subplot, else false
        for keyG in self._setup_options.keys(): # TODO: cleanup to list comprehension
            any_uses_subplots = False
            for keyT in self._setup_options[keyG]["traces"].keys(): # iterate through traces
                if self._setup_options[keyG]["traces"][keyT]["T"] == "secondary":
                    any_uses_subplots = True
            self._setup_options[keyG]["options"]["subplots"] = any_uses_subplots
                    
        # stores all the raw data from the training loop (losses, etc...)
        self._store = self._make_store()
        if (model is not None) and (input_data is not None):
            model_summary = summary(
                model, 
                input_data = input_data,
                col_names  = ["num_params"],
                col_width  = 12,
                verbose    = False,
            )
            self._store["summary"] = str(model_summary)
        else: 
            self._store["summary"] = "no information available!"
        
        # links an unique identifier to the respective trace number for each trace
        self._n2t = { 
            "g1": {},
            "g2": {},
            "g3": {},
        }
        
        # TODO: add an n2a dict for doing the same with annotations!

        # this is the container for the actual plotter app
        self._app = make_plotter_app(self._setup_options, self._store, self._n2t)

    def _make_store(self):
        store = {}
        
        # TODO: change so that this actually uses the number at the end of traceX instead of a counter!
        g, t = 1, 1
        for keyG in self._setup_options.keys():
            store[f"g{g}"] = {}
            
            for keyT in self._setup_options[keyG]["traces"].keys():
                store[f"g{g}"][f"t{t}_x"]       = []
                store[f"g{g}"][f"t{t}_y"]       = [] 
                store[f"g{g}"][f"t{t}_yMin"]    = float("inf")
                store[f"g{g}"][f"t{t}_yMinNew"] = False
                store[f"g{g}"][f"t{t}_yMax"]    = float("-inf")
                store[f"g{g}"][f"t{t}_yMaxNew"] = False
                
                if self._setup_options[keyG]["traces"][keyT]["E"] is True:
                    store[f"g{g}"][f"t{t}_yLo"] = []
                    store[f"g{g}"][f"t{t}_yHi"] = []
                
                if self._setup_options[keyG]["options"]["downsamplex"] is not False:
                    totalX = self._setup_options[keyG]["options"]["totalx"]
                    NxDown = self._setup_options[keyG]["options"]["downsamplex"]
                    store[f"g{g}"][f"t{t}_xDown"] = np.linspace(0, totalX, NxDown)
                    
                t += 1
            t  = 1
            g += 1
        
        # processing speed containers
        store["proc"]          = {}
        store["proc"]["speed"] = deque(maxlen=10)
        store["proc"]["t0"]    = None
        store["proc"]["t1"]    = None
        
        return store
        
    def add_data(self, graph: int, trace: int, x: float, y: float, yStdLo: float = None, yStdHi: float = None):
        # TODO do robust sanitizing of input data! (like detach, cpu, remove Nans, etc...)
        
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

