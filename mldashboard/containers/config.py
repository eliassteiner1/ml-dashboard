from dataclasses import dataclass


@dataclass
class GraphTrace:
    """ each trace that's added to a graph will need these config params """
    name: str # legend name
    color: str # rgb(x, x, x) or rgba(x, x, x, a) or css name
    order: str # {primary, secondary}
    errors: bool # show error bands
    point: bool = True # show glowing endpoint
    shape: str = "spline" # {spline, linear}
    
@dataclass
class GraphOptions:
    title: str # main title of this graph
    subplots: bool # flag for if the plot needs to have subplots (seems to be decided by whether a trace is secondary)
    xlabel: str # label for x axis
    ylabel1: str # label for primary y axis
    ylabel2: str # label for secondary y axis
    showmax: bool | str # can put a trace name here to show it's maximum value
    showmin: bool | str # can put a trace name here to show it's minimum value
    totalx: int # basically xrange max, number of samples
    downsamplex: bool | int # for downsampling the plots to a fixed resolution to conserve resources

    
@dataclass
class Graph:
    options: GraphOptions
    traces: list[GraphTrace]