import plotly.io as pio
import plotly.graph_objects as go
import json

# Define a custom template
custom_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(20, 20, 20, 1.0)",  # Transparent background
        plot_bgcolor="rgba(20, 20, 20, 1.0)",   # Transparent plot area
        font=dict(
            family="JetBrains Mono",  # Set all text to JetBrains Mono
            color="rgb(200, 200, 200)"  # Text color
        ),
        
        xaxis=dict(
            showgrid=True,  # Show gridlines
            gridcolor="rgb(100, 100, 100)",  # Gridline color
            gridwidth=1,  # Gridline width
            zeroline=True,  # Show zeroline
            zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
            zerolinewidth=2,  # Zeroline width
            ticklabelstandoff=6,
        ),
        
        yaxis=dict(
            showgrid=True,  # Show gridlines
            gridcolor="rgb(100, 100, 100)",  # Gridline color
            gridwidth=1,  # Gridline width
            zeroline=True,  # Show zeroline
            zerolinecolor="rgb(100, 100, 100)",  # Zeroline color
            zerolinewidth=2,  # Zeroline width
            ticklabelstandoff=6,
        ),
        
        margin=dict(l=50, r=50, t=50, b=50),  # Set margins
    )
)  

# Set the default template globally
pio.templates["my_custom_template"] = custom_template
pio.templates.default = "my_custom_template"

# Now, all new figures will use this template
fig = go.Figure()
fig.add_trace(go.Scatter(
    x = [-1, 2, 3, 4, 5],
    y = [-7, 8, 9, 10, -2],
)
)
fig.show()

# Save template to a JSON file
with open("custom_template.json", "w") as f:
    json.dump(custom_template.to_plotly_json(), f)
 
    
### 
# Load and apply the template in another script
with open("custom_template.json", "r") as f:
    custom_template = go.layout.Template(json.load(f))
pio.templates["my_custom_template"] = custom_template
