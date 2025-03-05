### IMPORTS ############################################################################################################
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ml_dashboard.dash.components import make_graphcard
from ml_dashboard.dash.components import make_flexgraph


def make_plotter_app(setup_options: dict, store: dict, n2t: dict):
    
    app = Dash(
        __name__,
        external_stylesheets = [],
        assets_folder        = "./assets" # specify assets folder because project structure is different from default
    )
    
    graph1 = make_flexgraph(setup_options, store, n2t, graphnr=1)
    graph2 = make_flexgraph(setup_options, store, n2t, graphnr=2)
    graph3 = make_flexgraph(setup_options, store, n2t, graphnr=3)
    
    app.layout = html.Div(
        className = "main-grid",
        children = [
            make_graphcard(title = "title A", gridbox = "A", graphid = "graph1", graphfig = graph1),
            make_graphcard(title = "title B", gridbox = "B", graphid = "graph2", graphfig = graph2),
            make_graphcard(title = "title C", gridbox = "C", graphid = "graph3", graphfig = graph3),
            html.Div(
                className = "card main-grid-boxD",
                children  = [
                    html.Div(className = "header", children = ["title card D"]),
                    html.Div(className = "body",   children = ["somebodytext"]),
                ],
            ),
            html.Div(
                className = "card main-grid-boxE",
                children  = [
                    html.Div(className = "header", children = ["title card E"]),
                    html.Div(className = "body",   children = ["somebodytext"]),
                ],
            ),
            
            dcc.Interval(
                id          = "ud_interval-1",
                interval    = 1000,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud_interval-2",
                interval    = 1000,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud_interval-3",
                interval    = 1000,
                n_intervals = 0,
            ),
            
            dcc.Store(id="chkps-1", data=-1),
            dcc.Store(id="chkps-2", data=-1),
            dcc.Store(id="chkps-3", data=-1),
        ]
    )
    
    return app