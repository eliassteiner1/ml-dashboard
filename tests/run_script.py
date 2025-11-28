import os
import sys
from   pathlib import Path
import time

import numpy as np
import torch.nn as nn

sys.path.insert(0, os.path.normcase(Path(__file__).resolve().parents[1]))
from mldashboard.plotter import DashPlotter
from mldashboard.containers.setupconfig import Config, GraphConfig, TraceConfig


class DummyNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.mlp = nn.Sequential(
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
        )

        self.layer1 = nn.Linear(100, 20)
        self.layer2 = nn.Linear(20, 10)
        self.layer3 = nn.Linear(10, 1)
        self.activation = nn.ReLU()

    def forward(self, x):
        x = self.mlp(x)

        x = self.activation(self.layer1(x))
        x = self.activation(self.layer2(x))
        x = self.layer3(x)

        return x

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear") # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")

    totalx = 1.0
    
    cfg = Config(
        graph1=GraphConfig(
            title   = "The Plot in Card A (first one)",
            xlabel  = "xaxis 1",
            ylabel1 = "yaxis 1",
            ylabel2 = False,
            showmax = False,
            showmin = 1, # second trace xD # TODO: this is a bit cumbersome
            totalx  = totalx,
            nxdown  = 1_000,
            traces  = [  
                TraceConfig(name="trace 1", color="firebrick", errors=True),
                TraceConfig(name="trace 2", color="seagreen"),
            ]
        ),
        graph2=GraphConfig(
            title   = "The Plot in Card B (second one)",
            xlabel  = False,
            ylabel1 = "yaxis 1",
            ylabel2 = "yaxis 2",
            showmax = False,
            showmin = False,
            totalx  = totalx,
            nxdown  = 1_000,
            traces  = [  
                TraceConfig(name="trace 1", color="gold"),
                TraceConfig(name="trace 2", color="orange"),
                TraceConfig(name="trace 3", color="darkorchid", yaxis="secondary"),
            ]
        ),
        graph3=GraphConfig(
            title   = "The Plot in Card C (third one)",
            xlabel  = False,
            ylabel1 = "yaxis 1",
            ylabel2 = "yaxis 2",
            showmax = False,
            showmin = False,
            totalx  = totalx,
            nxdown  = 1_000,
            traces = [
                TraceConfig(name="trace 1", color="steelblue"),
                TraceConfig(name="trace 2", color="olive", yaxis="secondary"),
            ]
        ),
    )
    

    PLOTTER = DashPlotter(CONFIG=cfg, model=DummyNet())
    PLOTTER.run_script()
    
    rnd = lambda: np.random.rand()
    time.sleep(3)
    N = 2_000
    
    y1_old = 0
    y2_old = 0
    
    for i in np.linspace(0, totalx, N):
        PLOTTER.batchtimer("start")
        
        # plot 1
        PLOTTER.add_data(
            graph_nr=1, trace_nr=0, 
            x=i, 
            y= 5*(i/totalx) * np.sin(40*i/totalx) + 2*rnd() +10, 
            yStdLo=0.5*rnd()+1.5, 
            yStdHi=0.5*rnd()+1.5
        )
        PLOTTER.add_data(graph_nr=1, trace_nr=1, 
                         x=i, y=(2 - i/totalx)*(5 + rnd()))
        
        
        # plot 2
        PLOTTER.add_data(
            graph_nr=2, trace_nr=0,
            x=i, y=5*(i/totalx) * np.sin(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            graph_nr=2, trace_nr=1,
            x=i, y=5*(i/totalx) * np.cos(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            graph_nr=2, trace_nr=2,
            x=i, y=np.exp(3*i/totalx) + 2.0*np.exp(i/totalx)*rnd()
        )
        
        # plot 3
        PLOTTER.add_data(
            graph_nr=3, trace_nr=0,
            x=i, y=y1_old + 0.2*rnd()
        )
        PLOTTER.add_data(
            graph_nr=3, trace_nr=1,
            x=i, y=y2_old + 0.2*rnd()
        )
        
        y1_old += 0.08*(rnd() - 0.5)
        y2_old += 0.08*(rnd() - 0.5)
        
        time.sleep(0.01)
        PLOTTER.batchtimer("stop", batch_size=100)
   
    PLOTTER.run_script_spin()
        

