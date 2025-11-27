from dataclasses import dataclass
from dataclasses import field

# TODO: maybe merge this into datastore? otherwise there are going to be a looot of classes

@dataclass
class TraceN2Id:
    main:    int = None
    minline: int = None
    maxline: int = None
    lo:      int = None
    hi:      int = None
    point:   int = None
    
    _parent: "GraphN2Id" = None
    
    def _register_parent(self, parent: "GraphN2Id"):
        self._parent = parent
        return self

    def register(self, attr: str):
        if getattr(self, attr) is not None:
            raise ValueError(f"{attr} already registered")
        else:
            new_id = self._parent._get_new_id()
            setattr(self, attr, new_id)

@dataclass
class GraphN2Id:
    traces: list[TraceN2Id] = field(default_factory=list)
    
    _object_counter: int = 0
    
    def _get_new_id(self):
        temp_counter = self._object_counter
        self._object_counter += 1
        return temp_counter
    
@dataclass
class MapN2Id:
    graph1: GraphN2Id = field(default_factory=GraphN2Id)
    graph2: GraphN2Id = field(default_factory=GraphN2Id)
    graph3: GraphN2Id = field(default_factory=GraphN2Id)
    

