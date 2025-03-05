import numpy as np
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   ml_dashboard.utils import adjust_alpha

def make_flexgraph():
    
    # some global customization params. TODO: make nicely controllable globally
    padding_factor = 0.03
    smoothing      = 0.60
    GRAY_LIGHT     = "rgb(200, 200, 200)"
    GRAY_DARK      = "rgb(100, 100, 100)"
    

    graph = go.Figure()
    
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
    
    return graph
