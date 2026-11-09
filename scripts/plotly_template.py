from dataclasses import dataclass, replace
import plotly.graph_objects as go
import plotly.io as pio


# ==============================================================================
# CONFIG TOKENS ================================================================
# ==============================================================================
@dataclass(frozen=True)
class Tokens:
    # surfaces & text
    bg: str = "#ffffff"
    fg: str = "#2b2b2b"          # main text
    muted: str = "#777777"       # tick labels, secondary text
    grid: str = "#ececec"
    axis: str = "#bdbdbd"
    # data colors
    colorway: tuple = (
        "#1a46b0", 
        "#d3800f", 
        "#018267", 
        "#a93119", 
        "#d27ba7", 
        "#3ea7dd",
        "#7e66b7",
        "#81bb74",
    )
    sequential: str = "Viridis"
    diverging: str = "RdBu"
    # typography
    font: str = "JetBrains Mono"
    size: int = 12
    title_size: int = 16
    # marks
    line_width: float = 2
    marker_size: int = 6

LIGHT = Tokens()
DARK = replace(LIGHT, 
    bg="#16181d", 
    fg="#e6e6e6", 
    muted="#9a9a9a", 
    grid="#2a2d34", 
    axis="#4a4e57",
    colorway= [
        "#3b66c4", 
        "#d37e00", 
        "#007b60", 
        "#c02b06", 
        "#cc4f95", 
        "#489ecd",
        "#9b70f3",
        "#70a365", 
    ]
)



# ==============================================================================
# BUILD TEMPLATE TREE ==========================================================
# ==============================================================================
def _axis(t: Tokens) -> dict:
    return dict(
        showgrid=True, 
        gridcolor=t.grid, 
        gridwidth=2,
        minor=dict(showgrid=True, nticks=5),
        zeroline=False,
        showline=False, 
        linecolor=t.axis, 
        ticks="",
        tickfont=dict(color=t.muted, size=12), 
        title_font=dict(color=t.fg),
        tickformat=".3s",
        title_standoff=30,
        rangemode="tozero",
    )

def _scene_axis(t: Tokens) -> dict:
    return dict(
        gridcolor=t.grid, 
        showbackground=False,
        showgrid=False,
        zeroline=False, 
        showline=True,
        linecolor=t.axis, 
        linewidth=2,
        tickfont=dict(color=t.muted),
        # tickformat=".3s",
        showspikes=False,
    )

def build(t: Tokens) -> go.layout.Template:
    # helper to construct the config tree. building it from the tokens makes easily configurable

    
    return go.layout.Template(
        
        # everything from "fig.update_layout()" ================================
        layout=dict(
            
            # global look -----------------
            font=dict(family=t.font, size=t.size, color=t.fg),
            paper_bgcolor=t.bg, 
            plot_bgcolor=t.bg,
            margin_pad=10,
            height=800,
            margin=dict(l=60+20, r=20+20, t=70, b=60+20),         
        
        
            
            
            colorway=list(t.colorway),
            colorscale=dict(sequential=t.sequential, diverging=t.diverging),
            hoverlabel=dict(font_family=t.font),
            # height, width
            # autosize
            # hovermode
            # modebar 
            # dragmode 
            # separators
            
            # title ----------------
            title=dict(
                x=0.00,
                y=1.00,
                pad=dict(l=20, t=20),
                font_size=t.title_size
            ),
            # can also do positioning etc of title
            
            # legend ---------------
            legend=dict(
                bgcolor=t.bg, 
                bordercolor=t.bg,
                borderwidth=8,
                orientation="v", 
                x=1.01,
                y=1.01, 
                xanchor="right",
                yanchor="top", 
                font=dict(size=12),
            ),
            
            # positioning and sizing
            
            # 2D axes -----------------------
            xaxis=_axis(t), yaxis={**_axis(t), "tickangle": -90},
            # lines, ticks, axis title, zeroline, grid
            
            # 3D Axes (=scenes) --------------------
            scene=dict(
                xaxis=_scene_axis(t), 
                yaxis=_scene_axis(t), 
                zaxis=_scene_axis(t),
                aspectmode="cube"
            ),
            # like the 2d but also has bg, spikes
            # camera (default angle)
            # aspectmode / ratio
            
            # coloraxis ---------------
            
            # annotation defs ----------
   
            
        ),
        # per trace settings (markers, etc) ====================================
        data=dict(
            # mostly for marker, line, colors, 
            scatter=[go.Scatter(line_width=t.line_width, marker_size=t.marker_size)],
            scatter3d=[go.Scatter3d(marker_size=t.marker_size / 2)],
            surface=[go.Surface(showscale=False)]
        ),
    )



# ==============================================================================
# API (TO APPLY TEMPLATE) ======================================================
# ==============================================================================
def register() -> None:
    # this build one json tree that can be used as a template by feeding it the dark or light config tokens
    pio.templates["mine_light"] = build(LIGHT)
    pio.templates["mine_dark"] = build(DARK)

def use(name: str = "mine_light") -> None:
    # this gets the template and then applies it with pio
    register()
    pio.templates.default = name