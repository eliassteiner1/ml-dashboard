### IMPORTS ############################################################################################################
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ml_dashboard.dash.components import make_graphcard
from ml_dashboard.dash.components import make_flexgraph


def make_plotter_app():
    
    app = Dash(
        __name__,
        external_stylesheets = [],
        assets_folder        = "./assets" # specify assets folder because project structure is different from default
    )
    
    testgraph = make_flexgraph()
    
    app.layout = html.Div(
        className = "main-grid",
        children = [
            make_graphcard(title = "title A", gridbox = "A", graphid = "graph1", graphfig = testgraph),
            make_graphcard(title = "title B", gridbox = "B", graphid = "graph2", graphfig = testgraph),
            make_graphcard(title = "title C", gridbox = "C", graphid = "graph3", graphfig = testgraph),

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
                id          = "ud-interval",
                interval    = 1000,
                n_intervals = 0,
            ),
            dcc.Store(id="checkpoint", data=-1),
        ]
    )
    
    return app