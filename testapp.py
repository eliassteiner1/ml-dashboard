# standard library imports
import os
import sys
import threading
import time
import copy
import json
# third-party library imports
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


store = {
    "x": [],
    "y": [],
    "knownrange": [0, 1],
    "x_down": np.linspace(0, 1, 1000),
}

graph = make_subplots(specs=[[{"secondary_y": True}]])
graph.update_layout(
    paper_bgcolor="rgba(20, 20, 20, 1.0)",  # Transparent background
    plot_bgcolor="rgba(20, 20, 20, 1.0)",   # Transparent plot area
    font=dict(
        family="JetBrains Mono",  # Set all text to JetBrains Mono
        color="rgb(200, 200, 200)"  # Text color
    ),
    margin=dict(l=50, r=50, t=50, b=50),  # Set margins
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
            interval    = 500,
            n_intervals = 0,
        ),
        dcc.Store(id="checkpoint", data=0),
    ]
)

@app.callback(
    Output("graph-cardA", "figure"),
    Output("graph-cardB", "figure"),
    Output("graph-cardC", "figure"),
    Output("checkpoint", "data"),
    Input("ud-interval", "n_intervals"),
    State("checkpoint", "data"),
    prevent_initial_call=True
)
def update_graph_patched(n, old_chkp):
    
    if len(store["x"]) <= 0:
        return no_update
    
    # downsample data
    lastidx = np.searchsorted(store["x_down"], store["x"][-1])-1 # find last coarse grid point with full data avail!
    x_down  = store["x_down"]
    y_down  = np.interp(x_down[0:lastidx+1], store["x"], store["y"])
    
    # grab index of newest available datapoint
    new_chkp = len(store["x"])
    
    
    ptch = Patch()
    # maybe add some if block, that REPLACES data when old chkp is 0, to remove any initial Nones
    if new_chkp > old_chkp: # only update if new data is available
        # Append new data to the first trace (index 0)
        ptch["data"][0]["x"].extend(store["x"][old_chkp:new_chkp])
        ptch["data"][0]["y"].extend(store["y"][old_chkp:new_chkp])
        
        # change the trace data for the endpoint trace (idx 1)
        ptch["data"][1]["x"] = [store["x"][new_chkp-1]]
        ptch["data"][1]["y"] = [store["y"][new_chkp-1]]
        
        # change the trace data for the bestline trace (idx 2)
        new_min = min(store["y"][:new_chkp])
        ptch["data"][2]["y"] = [new_min]*2
        
        # modify the annotation for the bestvalue (apparently they also have indices like traces)
        ptch["layout"]["annotations"][0]["text"] = f"<b> lowest:<br> {new_min:07.4f}</b>"
        ptch["layout"]["annotations"][0]["y"] = new_min
    
        # patch the range (yaxis and yaxis2 for subplots)
        new_min = min(store["y"][:new_chkp])
        new_max = max(store["y"][:new_chkp])
        ptch["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = new_min - 1.0
        ptch["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = new_max + 1.0
    
    return ptch, ptch, ptch, new_chkp

    


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
    
    N = 100_00
    for i in range(N):
        
        
        store["x"].append(i/N)
        store["y"].append( 10* (i/N) * np.sin(i/N * 20) + np.random.randn() )
        
        time.sleep(0.01)
        
    run_script_spin()

    
