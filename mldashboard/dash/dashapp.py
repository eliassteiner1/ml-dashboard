### IMPORTS ############################################################################################################
import numpy as np
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dataclasses import fields


from mldashboard.dash.components import make_graphcard
from mldashboard.dash.components import make_flexgraph
from mldashboard.dash.components import callback_generate_flexgraph_patch
from mldashboard.dash.components import callback_update_proc_speed

from ..containers.setupconfig import SetupConfig, GraphConfig
from ..containers.datastore import DataStore
from ..containers.name2id import MapN2Id

def make_plotter_app(CONFIG: SetupConfig, store: DataStore, n2id: MapN2Id):
    
    # declare variable and handles -------------------------------------------------------------------------------------
    app = Dash(
        __name__,
        external_stylesheets = [],
        assets_folder        = "./assets" # specify assets folder because project structure is different from default
    )
    
    # temp uncomment
    graph1 = make_flexgraph(CONFIG.graph1, n2id.graph1)
    graph2 = make_flexgraph(CONFIG.graph2, n2id.graph2)
    graph3 = make_flexgraph(CONFIG.graph3, n2id.graph3)

    # app layout -------------------------------------------------------------------------------------------------------
    app.layout = html.Div(
        className = "main-grid",
        children = [
            make_graphcard(
                title = CONFIG.graph1.title, 
                gridbox = "A", 
                graphid = "graph-card-1", 
                graphfig = graph1
            ),
            make_graphcard(
                title = CONFIG.graph2.title, 
                gridbox = "B", 
                graphid = "graph-card-2", 
                graphfig = graph2
            ),
            make_graphcard(
                title = CONFIG.graph3.title, 
                gridbox = "C", 
                graphid = "graph-card-3", 
                graphfig = graph3
            ),
            html.Div(
                className = "card main-grid-boxD",
                children  = [
                    html.Div(className = "header", children = ["Processing Speed"]),
                    html.Div(
                        className = "body proc-speed",
                        id        = "proc-speed-text",
                        children  = [f"---'---.-- samples/sec"],
                    ),
                ],
            ),
            html.Div(
                className = "card main-grid-boxE",
                children  = [
                    html.Div(className = "header", children = ["Model Summary"]),
                    html.Div(className = "body model-info",   children = [store.msummary]),
                ],
            ),
            
            dcc.Interval(
                id          = "ud-interval-1",
                interval    = 500, #TODO rout to config file
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud-interval-2",
                interval    = 500,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud-interval-3",
                interval    = 500,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud-interval-4",
                interval    = 500,
                n_intervals = 0,
            ),
            # checkpoints are in stores so that they are "race condition" safe, or rather multithreading-safe?
            # initialize the checkpoint for each trace to -1
            dcc.Store(id="g1-chkp-traces", data=[-1]*len(CONFIG.graph1.traces)),
            dcc.Store(id="g2-chkp-traces", data=[-1]*len(CONFIG.graph2.traces)),
            dcc.Store(id="g3-chkp-traces", data=[-1]*len(CONFIG.graph3.traces)),
        ]
    )
    
    # callbacks --------------------------------------------------------------------------------------------------------
    
    # # temp uncomment
    # @app.callback(
    #     [Output("graph-card-1", "figure"), Output("g1-chkp-traces", "data")],
    #     [Input("ud-interval-1", "n_intervals")],
    #     [State("g1-chkp-traces", "data")]
    # )
    # def update_graph_1(n, chkp_traces):
    #     return callback_generate_flexgraph_patch(CONFIG, store, n2id, chkp_traces, graphnr=1)
    
    # @app.callback(
    #     [Output("graph-card-2", "figure"), Output("g2-chkp-traces", "data")],
    #     [Input("ud-interval-2", "n_intervals")],
    #     [State("g2-chkp-traces", "data")]
    # )
    # def update_graph_2(n, chkp_traces):
    #     return callback_generate_flexgraph_patch(CONFIG, store, n2id, chkp_traces, graphnr=2)
    
    # @app.callback(
    #     [Output("graph-card-3", "figure"), Output("g3-chkp-traces", "data")],
    #     [Input("ud-interval-3", "n_intervals")],
    #     [State("g3-chkp-traces", "data")]
    # )
    # def update_graph_3(n, chkp_traces):
    #     return callback_generate_flexgraph_patch(CONFIG, store, n2id, chkp_traces, graphnr=3)
    
    # @app.callback(
    #     [Output("proc-speed-text", "children")],
    #     [Input("ud-interval-4", "n_intervals")]
    # )
    # def update_proc_speed(n):
    #     return callback_update_proc_speed(store)

    
    
    return app