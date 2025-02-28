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
from dash import Dash, Input, Output, State, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots



store = {
    "x": [],
    "y": [],
}

graph = go.Figure()
graph.update_layout(
    paper_bgcolor="rgba(20, 20, 20, 1.0)",  # Transparent background
    plot_bgcolor="rgba(20, 20, 20, 1.0)",   # Transparent plot area
    font=dict(
        family="JetBrains Mono",  # Set all text to JetBrains Mono
        color="rgb(200, 200, 200)"  # Text color
    ),
    margin=dict(l=50, r=50, t=50, b=50),  # Set margins
    uirevision="const",
    
    xaxis=dict(
        showgrid=True,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
        zerolinewidth=2,  # Zeroline width
        ticklabelstandoff=6,
        range=[0, 1],
    ),
    
    yaxis=dict(
        showgrid=True,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
        zerolinewidth=2,  # Zeroline width
        ticklabelstandoff=6,
    ),
)
graph.add_trace(go.Scatter(
    x = store["x"],
    y = store["y"],
    mode = "lines",
))
 


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
                        id         = "graph-card1",
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
                html.Div(className = "header", children = ["title card B"]),
                html.Div(className = "body",   children = ["somebodytext"])
            ],
        ),
        html.Div(
            className = "card main-grid-boxC",
            children  = [
                html.Div(className = "header", children = ["title card C"]),
                html.Div(className = "body",   children = ["somebodytext"])
            ],
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
    ]
)

@app.callback(
    Output("graph-card1", "figure"),
    Input("ud-interval", "n_intervals")
)
def update_graph_full(n):
    graph.data[0].x = store["x"]
    graph.data[0].y = store["y"]
    return graph


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
                use_reloader = False     
            )
        threading.Thread(target = _run, daemon = True).start()

    run_app(app)
    
    N = 10000
    for i in range(N):
        store["x"].append(i/N)
        store["y"].append(np.sin(i/N * 10) + np.random.randn())
        time.sleep(0.01)
        
    run_script_spin()

    
