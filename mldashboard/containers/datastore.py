import dataclasses
from   dataclasses import dataclass
from   dataclasses import field
from   dataclasses import fields
from   collections import deque
import numpy as np
from   numpy.typing import NDArray
from   typing import Callable


@dataclass
class ProcsData:
    speed: deque = field(default_factory=lambda: deque(maxlen=10))
    t0:    float = None
    t1:    float = None
   
@dataclass
class TraceData():
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
class BaseHandle2Id:
    """ generic id registry. gives plotly element numbers (given out sequentially) a nice handle for convenience """
    
    _parent: "GraphStore"    = None
    _new_id_handle: Callable = None
    _REGISTERABLE: set       = None

    def __post_init__(self) -> None:
        # automatically discover the allowed set of all the registrable attributes (everything "non-private")
        self._REGISTERABLE = {fd.name for fd in fields(self) if (fd.name.startswith("_") is not True)}

    def _register_parent(self, parent: "GraphStore", new_id_handle: Callable):
        self._parent = parent
        self._new_id_handle = new_id_handle
    
    def register(self, attr: str) -> None:
        if attr not in self._REGISTERABLE:
            raise AttributeError(f"{attr} is not a registerable field!")
        if getattr(self, attr) is not None:
            raise ValueError(f"{attr} already registered!")
        
        new_id = self._new_id_handle()
        setattr(self, attr, new_id)

@dataclass
class TraceT2Id(BaseHandle2Id):
    main:    int = None
    minline: int = None
    maxline: int = None
    lo:      int = None
    hi:      int = None
    point:   int = None
    
@dataclass
class TraceA2Id(BaseHandle2Id):
    # TODO: what annotations are possible?
    minline: int = None
    maxline: int = None

@dataclass
class GraphStore:
    trc_data: list[TraceData] = field(default_factory=list)
    trc_t2id: list[TraceT2Id] = field(default_factory=list)
    trc_a2id: list[TraceA2Id] = field(default_factory=list)
    
    _plotly_trace_counter: int = 0
    _plotly_annot_counter: int = 0
    
    def _get_new_plotly_trace_id(self):
        temp_counter = self._plotly_trace_counter
        self._plotly_trace_counter += 1
        return temp_counter
    
    def _get_new_plotly_annot_id(self):
        temp_counter = self._plotly_annot_counter
        self._plotly_annot_counter += 1
        return temp_counter
    
    def add_trc_data(self, new_trc_data: TraceData):
        self.trc_data.append(new_trc_data)
    
    def add_trc_t2id(self):
        new_t2id = TraceT2Id()
        new_t2id._register_parent(self, self._get_new_plotly_trace_id)
        self.trc_t2id.append(new_t2id)
    
    def add_trc_a2id(self):
        new_a2id = TraceA2Id()
        new_a2id._register_parent(self, self._get_new_plotly_annot_id)
        self.trc_a2id.append(new_a2id)
    
@dataclass
class Store:
    # for storing the graph main data
    graph1: GraphStore = field(default_factory=GraphStore)
    graph2: GraphStore = field(default_factory=GraphStore)
    graph3: GraphStore = field(default_factory=GraphStore)
    
    # for storing everything procesing speed related
    procs: ProcsData   = field(default_factory=ProcsData)
    
    # torchinfo model summary string, can be overwritten if available
    msummary: str      = "no information available"

