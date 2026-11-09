import os
import sys
from   pathlib import Path
import time

import numpy as np
import torch.nn as nn

from mldashboard.plotter import DashPlotter
from mldashboard.containers.setupconfig import Config, GraphConfig, TraceConfig


# this just plays and feed the plotter artifically generated data

if __name__ == "__main__":
    print("\033[2J\033[3J\033[H", end="", flush=True) # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")

    totalx = 1.0
    
    cfg = Config(
        graph1=GraphConfig(
            title   = "The Plot in Card A (first one)",
            xlabel  = "xaxis 1",
            ylabel1 = "yaxis 1",
            ylabel2 = False,
            showmax = "trace0",
            showmin = "trace1", #1, # second trace xD # TODO: this is a bit cumbersome
            totalx  = totalx,
            nxdown  = 1_000,
            traces  = [  
                TraceConfig(name="trace 0", color="firebrick", errors=True),
                TraceConfig(name="trace 1", color="seagreen"),
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
                TraceConfig(name="trace 0", color="gold"),
                TraceConfig(name="trace 1", color="orange"),
                TraceConfig(name="trace 2", color="darkorchid", yaxis="secondary"),
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
                TraceConfig(name="trace 0", color="steelblue"),
                TraceConfig(name="trace 1", color="olive", yaxis="secondary"),
            ]
        ),
    )
    

    PLOTTER = DashPlotter(CONFIG=cfg)
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
            g_nr=1, t_nr=0, 
            x=i, 
            y= 5*(i/totalx) * np.sin(40*i/totalx) + 2*rnd() +10, 
            yerrLo=0.5*rnd()+1.5, 
            yerrHi=0.5*rnd()+1.5
        )
        PLOTTER.add_data(g_nr=1, t_nr=1, 
                         x=i, y=(2 - i/totalx)*(5 + rnd()))
        
        
        # plot 2
        PLOTTER.add_data(
            g_nr=2, t_nr=0,
            x=i, y=5*(i/totalx) * np.sin(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            g_nr=2, t_nr=1,
            x=i, y=5*(i/totalx) * np.cos(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            g_nr=2, t_nr=2,
            x=i, y=np.exp(3*i/totalx) + 2.0*np.exp(i/totalx)*rnd()
        )
        
        # plot 3
        PLOTTER.add_data(
            g_nr=3, t_nr=0,
            x=i, y=y1_old + 0.2*rnd()
        )
        PLOTTER.add_data(
            g_nr=3, t_nr=1,
            x=i, y=y2_old + 0.2*rnd()
        )
        
        y1_old += 0.08*(rnd() - 0.5)
        y2_old += 0.08*(rnd() - 0.5)
        
        
        time.sleep(0.01)
        PLOTTER.batchtimer("stop", batch_size=100)

    PLOTTER.run_script_spin()
        

