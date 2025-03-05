# standard library imports
import os
import sys
import threading
import time
import copy
import json
import bisect
# third-party library imports
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

def perf_timer(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"callback execution took: {(t1-t0)*1000:.4f}ms")
        return result
    return wrapper

def get_idx_next_smaller(seq: list | np.ndarray, new_element: float):

    if isinstance(seq, list):
        return np.clip(bisect.bisect_left(seq, new_element) - 1, a_min=0, a_max=None)
    if isinstance(seq, np.ndarray):
        return np.clip(np.searchsorted(seq, new_element) - 1, a_min=0, a_max=None)
    
    raise TypeError(f"the sequence input has to be either a list or and np.ndarray!") 

N_DOWN = 10_000
store = {
    "x": [],
    "y": [],
    "knownrange": [0, 1],
    "x_down": np.linspace(0, 1, N_DOWN),
}

graph = make_subplots(specs=[[{"secondary_y": True}]])
graph.update_layout(
    paper_bgcolor="rgba(20, 20, 20, 1.0)",  # Transparent background
    plot_bgcolor="rgba(20, 20, 20, 1.0)",   # Transparent plot area
    font=dict(
        family="JetBrains Mono",  # Set all text to JetBrains Mono
        color="rgb(200, 200, 200)"  # Text color
    ),
    margin=dict(l=50, r=50, t=30, b=30),  # Set margins
    uirevision="const",
    showlegend=True,
    
    xaxis=dict(
        showgrid=True,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
        zerolinewidth=2,  # Zeroline width
        ticklabelstandoff=6,
        autorangeoptions_minallowed=-0.05,
        autorangeoptions_maxallowed=1.05,
    ),
    
    yaxis=dict(
        title="yaxis 1",
        showgrid=True,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
        zerolinewidth=4,  # Zeroline width
        ticklabelstandoff=6,
    ),
    
    yaxis2=dict(
        title="yaxis 2",
        showgrid=False,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="rgb(100, 0, 0)",  # Zeroline color
        zerolinewidth=2,  # Zeroline width
        ticklabelstandoff=6,
    ),
)
graph.update_layout(
    annotations = [
        dict(
            x         = 1.0, 
            y         = 0.0,
            xref      = "x", 
            yref      = "y",
            xanchor   = "left", 
            yanchor   = "middle",
            text      = f"<b> lowest:<br> {0.0:07.4f}</b>",
            font      = dict(
                family = "JetBrains Mono", 
                size = 14, 
                color = "white"
            ),
            showarrow = False,
            align     = "left",
            bgcolor   = "rgba(20, 20, 20, 1.0)",
        ),
    ],
)
graph.add_trace(go.Scatter( # 0: main trace
    x = [],
    y = [],
    mode = "lines",
    name = "main trace",
), secondary_y=False)
graph.add_trace(go.Scatter( # 1: endpoint
    x = [],
    y = [],
    mode = "markers",
    name = "endpoint",
    marker = dict(size=8, color="orange"),
), secondary_y=False)
graph.add_trace(go.Scatter( # 2: bestline
    x = [0, 1], # this can actually stay fixed
    y = [0, 0],
    mode = "lines+markers",
    name = "bestline",
    marker = dict(
        size=[20, 20], 
        color="gold", 
        symbol=["triangle-right", "triangle-left"], 
        opacity=1,
        line = dict(width=0)
    ),
), secondary_y=False)
graph.add_trace(go.Scatter(
    x = [None],
    y = [None],
    mode = "lines",
    name = "dummy secondary tr",
), secondary_y=True)

app = Dash(__name__, external_stylesheets=[], assets_folder="./assets")

app.layout = html.Div(
    className = "main-grid",
    children = [
        html.Div(
            className = "card main-grid-boxA",
            children  = [
                html.Div("someheader ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrtstuvwxyz", className="header"),
                html.Div(
                    className="body",
                    children=dcc.Graph(
                        id         = "graph-cardA",
                        className  = "graph",
                        responsive = True,
                        figure     = graph,
                    )
                ),
            ]
        ),
        html.Div(
            className = "card main-grid-boxB",
            children  = [
                html.Div("someheader ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrtstuvwxyz", className="header"),
                html.Div(
                    className="body",
                    children=dcc.Graph(
                        id         = "graph-cardB",
                        className  = "graph",
                        responsive = True,
                        figure     = graph,
                    )
                ),
            ]
        ),
        html.Div(
            className = "card main-grid-boxC",
            children  = [
                html.Div("someheader ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrtstuvwxyz", className="header"),
                html.Div(
                    className="body",
                    children=dcc.Graph(
                        id         = "graph-cardC",
                        className  = "graph",
                        responsive = True,
                        figure     = graph,
                    )
                ),
            ]
        ),
        html.Div(
            className = "card main-grid-boxD",
            children  = [
                html.Div(className = "header", children = ["title card D"]),
                html.Div(className = "body",   children = ["somebodytext"])
            ],
        ),
        html.Div(
            className = "card main-grid-boxE",
            children  = [
                html.Div(className = "header", children = ["title card E"]),
                html.Div(className = "body",   children = ["somebodytext"])
            ],
        ),
        
        dcc.Interval(
            id          = "ud-interval",
            interval    = 1000,
            n_intervals = 0,
        ),
        dcc.Store(id="checkpoint", data=-1),
    ]
)

@app.callback(
    [Output("graph-cardA", "figure"), Output("checkpoint", "data")],
    [Input("ud-interval", "n_intervals")], 
    [State("checkpoint", "data")],
    prevent_initial_call=True
)
def update_graph_patched(n, old_chkp):
    DO_DOWNSAMPLE = True
    ptch = Patch()
    
    if len(store["x"]) == 0: # exit when no data is available (avoids errors in subsequent code)
        return ptch, no_update 
    
    if DO_DOWNSAMPLE is False:
        # freeze the current length of the store, to handle data being appended while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
        idx_raw_newest = len(store["x"]) - 1 
        new_chkp       = idx_raw_newest
        
        # exit with no update if absolutely now new data samples are available
        if new_chkp <= old_chkp:
            return ptch, no_update
        
        # create the patch entry for appending data (tr idx 0)
        ptch["data"][0]["x"].extend(list( store["x"][old_chkp+1:new_chkp+1] ))
        ptch["data"][0]["y"].extend(list( store["y"][old_chkp+1:new_chkp+1] ))
        
    if DO_DOWNSAMPLE is True:
        # freeze the current length of the store, to handle data being appended while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
        idx_raw_newest = len(store["x"]) - 1 
        
        # determine the potential new checkpoint: finds the index of the next smaller element (to latest raw x) in the downsampled x "grid". this will be the latest downsampled point that is fully covered by raw data
        new_chkp = get_idx_next_smaller(store["x_down"], store["x"][idx_raw_newest])
        
        # exit with no update, if the new raw data doesn't cover a full downsampled x interval
        if new_chkp <= old_chkp:
            return ptch, no_update
        
        # find the lower end of the raw data that actually needs to be sampled. (just needs to fully cover the x downsampled interval from old_chkp to new_chkp, anything else is redundant)
        idx_raw_oldest = get_idx_next_smaller(store["x"], store["x_down"][old_chkp+1])
        
        # actually downsample the data
        y_down = np.interp(
            store["x_down"][old_chkp+1:new_chkp+1],
            store["x"][idx_raw_oldest:idx_raw_newest+1],
            store["y"][idx_raw_oldest:idx_raw_newest+1]
            )
        
        # create the patch entry for appending data (tr idx 0)
        ptch["data"][0]["x"].extend(list( store["x_down"][old_chkp+1:new_chkp+1] ))
        ptch["data"][0]["y"].extend(list( y_down ))

        # change the trace data for the endpoint trace (tr idx 1)
        ptch["data"][1]["x"] = [store["x_down"][new_chkp]]
        ptch["data"][1]["y"] = [y_down[-1]]
        
    return ptch, new_chkp

    


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear") # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")
    
    def run_script_spin():
        """For running the plotter in a script. Run this at the very end of the script. Keeps the app thread alive until the script is interrupted with ctrl+C to be able to view the data and interact with it."""
        
        print("Plotter dash app continues to run in the background. Press ctrl+C to stop.")
        try:
            while True:
                time.sleep(1) # lower cpu load!
        except KeyboardInterrupt:
            print("Terminating plotter dash app ...")
    
    def run_app(app):
        def _run():   
            app.run(
                host         = "127.0.0.1",
                port         = 8050,     
                debug        = True, 
                use_reloader = False # this is necessary, because hot reload is not possible in daemon thread    
            )
        threading.Thread(target = _run, daemon = True).start()

    run_app(app)
         
    time.sleep(2)
    
    N = 100_000
    for i in range(N):
        
        store["x"].append(i/N)
        store["y"].append( 10* (i/N) * np.sin(i/N * 20) + np.random.randn() )
        
        time.sleep(0.0008)
    
    print(store["x"][-1])
    run_script_spin()

    
