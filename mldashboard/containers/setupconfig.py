from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class TraceConfig:
    """ each trace that's added to a graph will need these config params """
    
    # name that is displayed in the legend (could maybe be automated to trace1, trace2, ... but bad practice)
    name: str 
    # rgb(x, x, x) or rgba(x, x, x, a) or css name (this could really be automated to select from a palette...)
    color: str 
    # to control whether a trace is drawn on a secondary y axis {primary, secondary}
    yaxis: str   = "primary"
    # flag to decide whether to show errorbands on a trance
    errors: bool = False
    # flag to decide whether to show the endpoint of a trace as a larger dot
    point: bool  = True
    # to control how the line is drawn. technically more possible but only linear and spline are nice {spline, linear}
    shape: str   = "spline"
    
    def _sanitize(self):
        raise NotImplementedError
        
        # TODO (
            # valid name, 
            # name length, 
            # valid color format, 
            # valid order, 
            # valid shape, 
            # check if flags are bool
        # )
             
@dataclass(frozen=True)
class GraphConfig:
    """ some general graph settings"""

    # settings related to all the traces of the graph (can be x many)
    traces:  list[TraceConfig] # TODO: maybe rename this? more in line with the store nomenclature
    # will just be the title at the top of this plot's card. no default makes sense
    title:   str  
    # basically xrange max, number of samples, has to be given!
    totalx:  int
    # for downsampling the plots to a fixed resolution to conserve resources (false or some resolution) 
    nxdown:  bool | int = False
    # flags to show one max or min value in the graph. can be none or ONE trace number for one of the options
    showmax: bool | int = False 
    showmin: bool | int = False 
    # these are just the labels for the plot axes. x is for sure not optional, but still, they could be None
    xlabel:  bool | str = False # for x axis
    ylabel1: bool | str = False # for primary y axis
    ylabel2: bool | str = False # for secondary y axis

    # flag for if the plot needs to have subplots
    @cached_property
    def has_subplots(self):
        return any(tr.yaxis=="secondary" for tr in self.traces)

        
    def _sanitize(self):
        raise NotImplementedError
        
        # TODO (
            # check at least a trace, check that it's even a list
            # valid title name, 
            # valid labels, 
            # label given at all?, 
            # only either showmax or showmin,
            # sane totalx range?, 
            # sance downsamplex resolution? (really has to be an integer or bool!)
            # subplots and showmin/showmax is exclusive!
        # )

@dataclass(frozen=True)
class Config:
    graph1: GraphConfig
    graph2: GraphConfig
    graph3: GraphConfig
    
    def sanitize(self):
        ...
        # TODO ipmlement