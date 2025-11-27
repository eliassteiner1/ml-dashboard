import os
import sys
from   pathlib import Path

sys.path.insert(0, os.path.normcase(Path(__file__).resolve().parents[1]))
from mldashboard.plotter import DashPlotter
from mldashboard.containers.setupconfig import SetupConfig, GraphConfig, TraceConfig


if __name__ == "__main__":
    os.system("cls" if os.name=="nt" else "clear")
    
    cfg = SetupConfig(
        graph1=GraphConfig(
            title  = "graph 1 title",
            xlabel="xaxis 1",
            ylabel1="yaxis 1",
            totalx = 10_000,
            nxdown = 20,
            traces = [  
                TraceConfig("g1 t1", "red"),
                TraceConfig("g1 t2", "green", yaxis="secondary"),
            ]
        ),
        graph2=GraphConfig(
            title  = "graph 2 title",
            xlabel="xaxis 2",
            ylabel1="yaxis 2",
            totalx = 10_000,
            traces = [ 
                TraceConfig("g2 t1", "red"),
                TraceConfig("g2 t2", "green"),
            ]
        ),
        graph3=GraphConfig(
            title  = "graph 3 title",
            xlabel="xaxis 3",
            ylabel1="yaxis 3",
            totalx = 10_000,
            nxdown = 10,
            traces = [
                TraceConfig("g3 t1", "red"),
                TraceConfig("g3 t2", "green"),
            ]
        ),
    )
    
    PLOTTER = DashPlotter(CONFIG=cfg)
    PLOTTER.run_script()
    PLOTTER.run_script_spin()
  