import os
import time
import numpy as np
from   pprint import pprint
from   ml_dashboard import DashPlotter



if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear") # start with an empty terminal
    print(f"\033[1m\033[38;2;51;153;102mrunning script {__file__}... \033[0m")
    
    totalx = 1_000
    setup_options = dict(
        graph1 = dict(
            options = dict(
                title       = "The Plot in Card A (first one)",
                subplots    = ...,
                xlabel      = "nr of samples processed total",
                ylabel1     = "losses",
                ylabel2     = False,
                showmax     = "trace2",
                showmin     = False,
                totalx      = totalx,
                downsamplex = False,
            ),
            traces  = dict(
                trace1 = dict(N = "loss_train", C = "firebrick", T = "primary", E = True,  P = True, S = "linear"),
                trace2 = dict(N = "loss_valid", C = "seagreen",  T = "primary", E = False, P = True, S = "linear"),
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
                downsamplex = False,
            ),
            traces  = dict(
                trace1 = dict(N = "eff. UdR", C = "gold",       T = "primary",   E = False, P = True, S = "linear"),
                trace2 = dict(N = "eff. LR",  C = "orange",     T = "primary",   E = False, P = True, S = "linear"),
                trace3 = dict(N = "batch sz", C = "darkorchid", T = "secondary", E = False, P = True, S = "linear"),
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
                downsamplex = False, 
            ),
            traces  = dict(
                trace1 = dict(N = "grad norm",   C = "steelblue", T = "primary",   E = False, P = True, S = "linear"),
                trace2 = dict(N = "weight norm", C = "olive",     T = "secondary", E = False, P = True, S = "linear"),  
            ),
        ),
    )
    
    PLOTTER = DashPlotter(setup_options)
    PLOTTER.run_script()
    

    
    rnd = lambda: np.random.rand()
    time.sleep(2)
    N = 100
    for i in np.linspace(0, totalx, N):
        
        PLOTTER.add_data(graph=1, trace=1, x=i, y=2*rnd(), yStdLo=rnd()+1, yStdHi=rnd()+1)
        
        time.sleep(0.1)
        
        
        
    PLOTTER.run_script_spin()
        