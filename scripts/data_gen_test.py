import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import h5py

import plotly_template
plotly_template.use(name="mine_dark")

def composite_func(x, y):  
    # low frequency: learned first
    smooth = 0.5 * (np.sin(1 * np.pi * x) * np.cos(0.8 * np.pi * y))  
    # high frequency: learned late
    r = np.sqrt((x + 0.25)**2 + (y - 0.25)**2)
    ripple = 0.15 * np.sin(50 * r) * np.exp(-5 * r)    
    # small, sharp feature        
    bump   = 0.8 * np.exp(-((x - 0.3)**2 + (y + 0.5)**2) / 0.01) 
    # nearly a step: sharp edge 
    ridge  = 0.3 * np.abs(np.tanh(20 * (y - 0.8 * x + 0.2))) 

    return smooth + ripple + bump + ridge


if __name__ == "__main__" :
    
    N = 100_000
    eps = 5e-2
    xy = np.random.uniform(-1, 1, size=(N, 2))
    z = composite_func(xy[:, 0], xy[:, 1]) + np.random.normal(loc=0, scale=eps, size=N)

    # fig = go.Figure(
    #     data = go.Scatter3d(
    #         x = xy[:, 0].ravel(), 
    #         y = xy[:, 1].ravel(), 
    #         z = z.ravel(),
    #         mode="markers",
    #         marker_size=1,
    #     ),
    #     layout=dict(
    #         height=800,
    #         margin=dict(l=20, r=20, b=20),
    #         scene=dict(aspectmode="data"),
    #     ),
    # )
    # fig.show()

    with h5py.File("./data/dataset.h5", "w") as f:
        f.create_dataset("input", data=xy.astype(np.float32))
        f.create_dataset("label", data=z.astype(np.float32))
        
    print("done with data generation - file saved!")