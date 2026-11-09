import numpy as np
import plotly.graph_objects as go

import importlib
import plotly_template

if __name__ == "__main__":
    
    # load & apply template
    importlib.reload(plotly_template)
    plotly_template.use(name="mine_dark")

    # draw some dummy figures to showcase
    rng = np.random.default_rng(0)
    x = np.linspace(-2, 2, 80)
    X, Y = np.meshgrid(x, x)
    Z = (np.sin(2 * X) * np.cos(Y) + 0.3 * X ) / 1000
    cats = list("ABCDE")

    go.Figure([go.Scatter(y=np.cumsum(rng.normal(size=60)), name=f"run {i*99}") for i in range(8)]).update_layout(title_text="Lines", xaxis_title="epoch - some longer title", yaxis_title="loss").show()

    go.Figure([go.Scatter(x=rng.normal(size=150) + 8000*i, y=rng.normal(size=150), mode="markers", name=f"cls {i}") for i in range(4)]).update_layout(title_text="Scatter").show()

    go.Figure(go.Surface(x=x, y=x, z=Z)).update_layout(title_text="Surface").show()

    go.Figure(go.Scatter3d(x=X.ravel(), y=Y.ravel(), z=Z.ravel(), mode="markers", marker_size=2)).update_layout(title_text="Scatter 3D").show()
