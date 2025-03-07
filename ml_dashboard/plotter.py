### IMPORTS ############################################################################################################
# standard library imports
import os
import sys
import threading
import time
from   collections import deque
# third-party library imports
import numpy as np
import torch
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from   plotly.subplots import make_subplots
import plotly.io as pio
# local library imports
from   ml_dashboard.dash import make_plotter_app

### DEFINITIONS ########################################################################################################

class DashPlotter:
    
    def __init__(self, setup_options: dict):
        
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
        
        # TODO: add proc speed stuff
        
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
            
    def batchtimer(self):
        # TODO: implement
        ...
        
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
        
    def run_script_spin(self):
        """For running the plotter in a script. Run this at the very end of the script. Keeps the app thread alive until the script is interrupted with ctrl+C to be able to view the data and interact with it."""
        
        print("Plotter dash app continues to run in the background. Press ctrl+C to stop.")
        try:
            while True:
                time.sleep(1) # lower cpu load!
        except KeyboardInterrupt:
            print("Terminating plotter dash app ...")

