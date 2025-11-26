from dataclasses import dataclass
from dataclasses import field


@dataclass
class TraceN2T:
    main:    int = None
    minline: int = None
    maxline: int = None
    lo:      int = None
    hi:      int = None
    point:   int = None
    
    _drawn_plotly_traces: int = 0
    
    



@dataclass
class GraphN2T:
    traces: list[TraceN2T] = field(default_factory=list)
    
    
@dataclass
class MapN2T:
    graph1: GraphN2T = field(default_factory=GraphN2T)
    graph2: GraphN2T = field(default_factory=GraphN2T)
    graph3: GraphN2T = field(default_factory=GraphN2T)