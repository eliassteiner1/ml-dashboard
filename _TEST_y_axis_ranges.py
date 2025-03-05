import numpy as np
import time
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

def determine_single_range(MAX: float, MIN: float, factor: float):
    """ MAX is max over all tracex and MIN is min over all traces """
    
    if MAX < MIN:
        raise ValueError(f"MAX should not be smaller than MIN! (got {MAX=}, {MIN=})")
    
    possible = [(1+factor)*MAX, -factor*MAX, (1+factor)*MIN, -factor*MIN]
    rng      = [min(possible), max(possible)]
    return rng

def determine_mixed_range(RNG1: list, RNG2: list):
    """ determines the best range for a subplot mixed y axis range so that both ranges have the same ratio of above zeroline and below zeroline spans. assumes max is > 0 and min is < 0!"""

    R1_ORIG = RNG1[1] / -RNG1[0] 
    R2_ORIG = RNG2[1] / -RNG2[0]
    RBAR    = (R1_ORIG * R2_ORIG)**0.5
    
    # new primary range
    if R1_ORIG > RBAR:
        RNG1[0] = (R1_ORIG / RBAR) * RNG1[0]
        RNG1[1] = RNG1[1]
    if R1_ORIG < RBAR:
        RNG1[0] = RNG1[0]
        RNG1[1] = (RBAR / R1_ORIG) * RNG1[1]
        
    # new secondary range
    if R2_ORIG > RBAR:
        RNG2[0] = (R2_ORIG / RBAR) * RNG2[0]
        RNG2[1] = RNG2[1]
    if R2_ORIG < RBAR:
        RNG2[0] = RNG2[0]
        RNG2[1] = (RBAR / R2_ORIG) * RNG2[1]
        
    return RNG1, RNG2
        

dataX = np.linspace(0, 1, 5000)
dataY1 = 5 * dataX * np.sin(dataX * 20) + np.random.rand(5000) + 5
dataY2 = 3 * dataX * np.cos(dataX * 20) + np.random.rand(5000) + 20

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
        zerolinewidth=1,  # Zeroline width
        ticklabelstandoff=6,
        autorangeoptions_minallowed=-0.05,
        autorangeoptions_maxallowed= 1.05,
    ),
    
    yaxis=dict(
        title="yaxis 1",
        showgrid=True,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="seagreen",  # Zeroline color
        zerolinewidth=4,  # Zeroline width
        ticklabelstandoff=6,
    ),
    
    yaxis2=dict(
        title="yaxis 2",
        showgrid=False,  # Show gridlines
        gridcolor="rgb(100, 100, 100)",  # Gridline color
        gridwidth=1,  # Gridline width
        zeroline=True,  # Show zeroline
        zerolinecolor="firebrick",  # Zeroline color
        zerolinewidth=4,  # Zeroline width
        ticklabelstandoff=6,
    ),
)
graph.add_trace(go.Scatter(
    x = dataX,
    y = dataY1,
    mode = "lines",
    name = "primary",
    line = dict(color = "seagreen")
    
),secondary_y=False)
graph.add_trace(go.Scatter(
    x = dataX,
    y = dataY2,
    mode = "lines",
    name = "secondary",
    line = dict(color = "firebrick")
    
),secondary_y=True)

# get preferred range for primary
range_primary = determine_single_range(MAX=max(dataY1), MIN=min(dataY1), factor=0.1)
# get preferred range for secondary
range_secondary = determine_single_range(MAX=max(dataY2), MIN=min(dataY2), factor=0.1)
# compute the mixed ranges
range_primary, range_secondary = determine_mixed_range(range_primary, range_secondary)

graph.update_layout(
    yaxis1 = dict(
        autorangeoptions_minallowed=range_primary[0],
        autorangeoptions_maxallowed=range_primary[1],
    ),
    yaxis2 = dict(
        autorangeoptions_minallowed=range_secondary[0],
        autorangeoptions_maxallowed=range_secondary[1],
    ),
)

graph.show()
