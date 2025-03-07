### IMPORTS ############################################################################################################
import numpy as np
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ml_dashboard.dash.components import make_graphcard
from ml_dashboard.dash.components import make_flexgraph
from ml_dashboard.dash.components import callback_generate_flexgraph_patch
from ml_dashboard.dash.components import callback_update_proc_speed

lorem = (
    " Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur lobortis feugiat diam, nec auctor mi feugiat at. Aliquam placerat quis purus a aliquam. Vivamus condimentum, ligula a pellentesque consequat, dolor sem pulvinar elit, eget facilisis mi ante a nulla. Donec laoreet orci neque, ac euismod nulla consectetur sed. Curabitur ullamcorper porttitor dapibus. Nam quis placerat risus, ac tempor nunc. Sed pharetra, dolor non varius viverra, ex elit varius dolor, vel dapibus orci erat quis lacus. Aenean ut arcu non nunc laoreet lacinia. Suspendisse egestas sapien est. Sed scelerisque sit amet dolor vitae convallis. Nulla facilisi. Etiam convallis sollicitudin volutpat.\n\n Aliquam erat volutpat. Morbi tristique pellentesque euismod. Integer lobortis libero mi, vitae accumsan tellus feugiat convallis. Integer laoreet erat ut suscipit lacinia. Morbi elementum arcu mi, vitae lobortis leo hendrerit vestibulum. Nullam viverra quam massa. Nulla blandit a dui a fermentum. Mauris enim ipsum, rutrum in iaculis eu, elementum vitae sapien. Nunc sollicitudin, orci eget accumsan mattis, ante arcu facilisis metus, ultrices scelerisque nisl arcu in risus. Vestibulum id libero ut ante pulvinar eleifend. Mauris vel accumsan velit. Donec sapien justo, molestie quis accumsan non, porttitor imperdiet risus. In nec consequat metus, a dapibus mauris. Suspendisse posuere suscipit nibh non fringilla. Suspendisse potenti. Maecenas malesuada, dui sed dapibus luctus, lorem elit luctus ipsum, vel rutrum orci nisl sit amet lectus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Fusce orci libero, consequat in est ullamcorper, vestibulum placerat diam. Fusce nec lacus vel ipsum porttitor congue eget vel lectus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. \n\n Suspendisse semper magna libero, ut scelerisque velit sodales non. Aliquam nunc augue, lacinia ac mattis in, mattis vel sapien. Vestibulum id consequat lacus. Integer luctus massa et turpis ultrices maximus. Nunc elementum augue ipsum, eget pellentesque elit aliquet a. Proin vel neque enim. Mauris sit amet ex dolor. Quisque quis dui porta, luctus nulla vitae, vulputate metus. Morbi consequat eros nec fermentum fringilla. Duis laoreet, purus ac efficitur venenatis, massa massa vulputate urna, in euismod risus diam sed ipsum. Aenean sit amet sapien enim. Nullam malesuada, purus pharetra dignissim vulputate, metus nibh ultrices ante, venenatis semper libero mi vitae justo. Proin ut tempor sem. Aenean semper et nulla id porta. Sed eu pretium eros, eu vestibulum nulla. Aliquam ornare dignissim dolor, eget volutpat sem ornare congue. Suspendisse pharetra aliquam mi. Nunc dictum felis ex, in posuere tellus tincidunt eget. Cras a tincidunt orci, ut pellentesque tellus. Quisque volutpat fringilla nunc in eleifend. Maecenas arcu lorem, volutpat et accumsan vulputate, porttitor non est. Morbi diam libero, semper sed orci et, feugiat sagittis quam. Proin vehicula lorem non semper vehicula. Aenean lobortis elementum ex, vel cursus turpis porta vitae. Sed vel lacus at massa imperdiet vulputate vitae in erat. Vivamus a ultrices augue, sit amet venenatis augue. Aliquam malesuada tempus risus, at pretium nunc sodales eu. Aliquam maximus sem tortor, sed iaculis nibh tincidunt sit amet. Nam porttitor bibendum lectus, sit amet semper enim convallis id. Donec lobortis ornare justo."
)


import time
def perf_timer(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"callback execution took: {(t1-t0)*1000:.4f}ms")
        return result
    return wrapper

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
            make_graphcard(title = "title A", gridbox = "A", graphid = "graph-card-1", graphfig = graph1),
            make_graphcard(title = "title B", gridbox = "B", graphid = "graph-card-2", graphfig = graph2),
            make_graphcard(title = "title C", gridbox = "C", graphid = "graph-card-3", graphfig = graph3),
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