import os
import time
import numpy as np
from   pprint import pprint
from   ml_dashboard import DashPlotter
import torch
import torch.nn as nn

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
    setup_options = dict(
        graph1 = dict(
            options = dict(
                title       = "The Plot in Card A (first one)",
                subplots    = ...,
                xlabel      = "number of samples processed total",
                ylabel1     = "losses",
                ylabel2     = False,
                showmax     = False,
                showmin     = "trace2",
                totalx      = totalx,
                downsamplex = 1000,
            ), 
            traces  = dict(
                trace1 = dict(N = "loss_train", C = "firebrick", T = "primary", E = True,  P = True, S = "spline"),
                trace2 = dict(N = "loss_valid", C = "seagreen",  T = "primary", E = False, P = True, S = "spline"),
            ),
        ),
        graph2 = dict(
            options = dict(
                title       = "The Plot in Card B (second one)",
                subplots    = ...,
                xlabel      = False,
                ylabel1     = "eff. rates",
                ylabel2     = "batch size",
                showmax     = False,
                showmin     = False,
                totalx      = totalx,
                downsamplex = 1000,
            ),
            traces  = dict(
                trace1 = dict(N = "eff. UdR", C = "gold",       T = "primary",   E = False, P = True, S = "spline"),
                trace2 = dict(N = "eff. LR",  C = "orange",     T = "primary",   E = False, P = True, S = "spline"),
                trace3 = dict(N = "batch sz", C = "darkorchid", T = "secondary", E = False, P = True, S = "spline"),
            ),  
        ),
        graph3 = dict(
            options = dict(
                title       = "The Plot in Card C (third one)",
                subplots    = ...,
                xlabel      = False,
                ylabel1     = "grad norm",
                ylabel2     = "weight norm",
                showmax     = False,
                showmin     = False,
                totalx      = totalx,
                downsamplex = 1000, 
            ),
            traces  = dict(
                trace1 = dict(N = "grad norm",   C = "steelblue", T = "primary",   E = False, P = True, S = "spline"),
                trace2 = dict(N = "weight norm", C = "olive",     T = "secondary", E = False, P = True, S = "spline"),  
            ),
        ),
    )
    
    PLOTTER = DashPlotter(setup_options, model=DummyNet())
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
            graph=1, trace=1, 
            x=i, 
            y= 5*(i/totalx) * np.sin(40*i/totalx) + 2*rnd() +10, 
            yStdLo=0.5*rnd()+1.5, 
            yStdHi=0.5*rnd()+1.5
        )
        PLOTTER.add_data(graph=1, trace=2, 
                         x=i, y=(2 - i/totalx)*(5 + rnd()))
        
        
        # plot 2
        PLOTTER.add_data(
            graph=2, trace=1,
            x=i, y=5*(i/totalx) * np.sin(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            graph=2, trace=2,
            x=i, y=5*(i/totalx) * np.cos(100*i/totalx) + 2*rnd() +10
        )
        PLOTTER.add_data(
            graph=2, trace=3,
            x=i, y=np.exp(3*i/totalx) + 2.0*np.exp(i/totalx)*rnd()
        )
        
        # plot 3
        PLOTTER.add_data(
            graph=3, trace=1,
            x=i, y=y1_old + 0.2*rnd()
        )
        PLOTTER.add_data(
            graph=3, trace=2,
            x=i, y=y2_old + 0.2*rnd()
        )
        
        y1_old += 0.08*(rnd() - 0.5)
        y2_old += 0.08*(rnd() - 0.5)
        
        time.sleep(0.01)
        PLOTTER.batchtimer("stop", batch_size=100)
   
    PLOTTER.run_script_spin()
        