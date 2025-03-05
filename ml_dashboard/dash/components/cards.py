### IMPORTS ############################################################################################################
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import plotly.graph_objects as go

def make_graphcard(title: str, gridbox: str, graphid: str, graphfig: go.Figure):
    card = html.Div(
        className = "card" + f" main-grid-box{gridbox}",
        children  = [
            html.Div(title, className="header"),
            html.Div(
                className="body",
                children=dcc.Graph(
                    id         = graphid,
                    className  = "graph",
                    responsive = True,
                    figure     = graphfig,
                )
            ),
        ]
    )
    
    return card
