import os
import sys
from   pathlib import Path

sys.path.insert(0, os.path.normcase(Path(__file__).resolve().parents[2]))
from mldashboard.containers.name2id import MapN2Id
from mldashboard.containers.name2id import GraphN2Id
from mldashboard.containers.name2id import TraceN2Id


if __name__ == "__main__":
    os.system("cls" if os.name=="nt" else "clear")

    asdf = MapN2Id()
    
    asdf.graph1.traces = [
        TraceN2Id()._register_parent(asdf.graph1),
        TraceN2Id()._register_parent(asdf.graph1),
    ]

    asdf.graph2.traces = [
        TraceN2Id()._register_parent(asdf.graph2),
        TraceN2Id()._register_parent(asdf.graph2),
    ]

    
    print(asdf.graph1._object_counter)
    
    asdf.graph1.traces[0].register("main")
    asdf.graph1.traces[0].register("point")
    
    print(asdf.graph1.traces[0].main)
    print(asdf.graph1.traces[0].point)
    print(asdf.graph1.traces[0].hi)
    
    print(asdf.graph1._object_counter)
    
    asdf.graph1.traces[0].register("main")
    
    
    