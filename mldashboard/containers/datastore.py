from   dataclasses import dataclass
from   dataclasses import field
from   collections import deque
import numpy as np
from   numpy.typing import NDArray



@dataclass
class ProcsStore:
    speed: deque = field(default_factory=lambda: deque(maxlen=10))
    t0:    float = None
    t1:    float = None
 
    
@dataclass
class TraceStore():
    
    # the main x and y data of this trace
    x:       list  = field(default_factory=list)
    y:       list  = field(default_factory=list)
    # stores the "range of y"
    ymin:    float = float("inf")
    ymax:    float = float("-inf")
    # stores if a new min or max was added to the y data (can probably be integrated better)
    ynewmin: bool  = False
    ynewmax: bool  = False
    
    # errorband, optional, check that nothing actually depends on this being optional! is easier if just inited
    ylo:     list  = None
    yhi:     list  = None
    
    # optional before, downsampled x range. maybe cached property?
    xdown:   NDArray = None
    
    def add_xdown(self, totalx: int, nxdown: int):
        self.xdown = np.linspace(0, totalx, nxdown)
        return
       
    def add_errorband(self):
        self.ylo = []
        self.yhi = []
        return


@dataclass
class GraphStore:
    traces: list[TraceStore] = field(default_factory=list)
    # t2id
    # a2id

@dataclass
class DataStore:
    
    # for storing the graph main data
    graph1:   GraphStore = field(default_factory=GraphStore)
    graph2:   GraphStore = field(default_factory=GraphStore)
    graph3:   GraphStore = field(default_factory=GraphStore)
    
    # for storing everything procesing speed related
    procs:    ProcsStore = field(default_factory=ProcsStore)
    
    # torchinfo model summary string, can be overwritten if available
    msummary: str = "no information available"
    