### IMPORTS ############################################################################################################
import numpy as np
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from mldashboard.dash.components import make_graphcard
from mldashboard.dash.components import make_flexgraph
from mldashboard.dash.components import callback_generate_flexgraph_patch
from mldashboard.dash.components import callback_update_proc_speed


def make_plotter_app(setup_options: dict, store: dict, n2t: dict):
    
    # declare variable and handles -------------------------------------------------------------------------------------
    app = Dash(
        __name__,
        external_stylesheets = [],
        assets_folder        = "./assets" # specify assets folder because project structure is different from default
    )
    
    graph1 = make_flexgraph(setup_options, store, n2t, graphnr=1)
    graph2 = make_flexgraph(setup_options, store, n2t, graphnr=2)
    graph3 = make_flexgraph(setup_options, store, n2t, graphnr=3)

    # initialize a checkpoint dict to -1 for each trace to pass to the dcc.stores (temporary)
    chkpts = []
    for graphXdict in setup_options.values():
        chkpts.append({f"t{int(keyT[-1])}": -1 for keyT in graphXdict["traces"].keys()})
    
    # app layout -------------------------------------------------------------------------------------------------------
    app.layout = html.Div(
        className = "main-grid",
        children = [
            make_graphcard(
                title = setup_options["graph1"]["options"]["title"], 
                gridbox = "A", 
                graphid = "graph-card-1", 
                graphfig = graph1
            ),
            make_graphcard(
                title = setup_options["graph2"]["options"]["title"], 
                gridbox = "B", 
                graphid = "graph-card-2", 
                graphfig = graph2
            ),
            make_graphcard(
                title = setup_options["graph3"]["options"]["title"], 
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
                    html.Div(className = "body model-info",   children = [store["summary"]]),
                ],
            ),
            
            dcc.Interval(
                id          = "ud-interval-1",
                interval    = 500,
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
            dcc.Store(id="chkp-graph-1", data=chkpts[0]),
            dcc.Store(id="chkp-graph-2", data=chkpts[1]),
            dcc.Store(id="chkp-graph-3", data=chkpts[2]),
        ]
    )
    
    # callbacks --------------------------------------------------------------------------------------------------------
    @app.callback(
        [Output("graph-card-1", "figure"), Output("chkp-graph-1", "data")],
        [Input("ud-interval-1", "n_intervals")],
        [State("chkp-graph-1", "data")]
    )
    def update_graph_1(n, chkp_dict):
        return callback_generate_flexgraph_patch(setup_options, store, n2t, chkp_dict, graphnr=1)
    
    @app.callback(
        [Output("graph-card-2", "figure"), Output("chkp-graph-2", "data")],
        [Input("ud-interval-2", "n_intervals")],
        [State("chkp-graph-2", "data")]
    )
    def update_graph_2(n, chkp_dict):
        return callback_generate_flexgraph_patch(setup_options, store, n2t, chkp_dict, graphnr=2)
    
    @app.callback(
        [Output("graph-card-3", "figure"), Output("chkp-graph-3", "data")],
        [Input("ud-interval-3", "n_intervals")],
        [State("chkp-graph-3", "data")]
    )
    def update_graph_3(n, chkp_dict):
        return callback_generate_flexgraph_patch(setup_options, store, n2t, chkp_dict, graphnr=3)
    
    @app.callback(
        [Output("proc-speed-text", "children")],
        [Input("ud-interval-4", "n_intervals")]
    )
    def update_proc_speed(n):
        return callback_update_proc_speed(store)

    
    
    return app