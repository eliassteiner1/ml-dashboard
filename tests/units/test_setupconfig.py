import os
import sys
from   pathlib import Path

sys.path.insert(0, os.path.normcase(Path(__file__).resolve().parents[2]))
from mldashboard.containers.setupconfig import Config
from mldashboard.containers.setupconfig import GraphConfig
from mldashboard.containers.setupconfig import TraceConfig


if __name__ == "__main__":
    os.system("cls" if os.name=="nt" else "clear")
    
    CFG = Config(
        graph1=GraphConfig(
            title  = "graph 1 title",
            totalx = 10_000,
            traces = [  
                TraceConfig("g1 t1", "red"),
                TraceConfig("g1 t2", "green", yaxis="secondary"),
            ]
        ),
        graph2=GraphConfig(
            title  = "graph 2 title",
            totalx = 10_000,
            traces = [ 
                TraceConfig("g2 t1", "red"),
                TraceConfig("g2 t2", "green"),
            ]
        ),
        graph3=GraphConfig(
            title  = "graph 3 title",
            totalx = 10_000,
            traces = [
                TraceConfig("g3 t1", "red"),
                TraceConfig("g3 t2", "green"),
            ]
        ),
    )
    
 
    print(CFG.graph1.has_subplots)
    print(CFG.graph1.has_subplots) # second time is cached!
    