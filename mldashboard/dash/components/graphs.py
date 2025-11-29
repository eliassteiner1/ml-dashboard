import numpy as np
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   mldashboard.utils import adjust_alpha

from ...containers.setupconfig import GraphConfig
from ...containers.datastore import Store, GraphStore, TraceData, TraceT2Id, TraceA2Id

# TODO: move the subfunctions out of this function, so that they don't use "globals" like they do now
def make_flexgraph(G_CFG: GraphConfig, g_store: GraphStore):
    
    # G_CFG is just one graph box of the main config
    # g_n2id is also just one graph-element of the n2id store
    
    # TODO, maybe make this one kind of plot-param dataclass, that can also be passed into the subfunctions
    # some global customization params
    PADDING_FACTOR = 0.03 # the additional space that is added + and - along the x axis
    SMOOTHING      = 0.60 # smooting factor of all the spline traces
    GRAY_LIGHT     = "rgb(200, 200, 200)"
    GRAY_DARK      = "rgb(80, 80, 80)"
    PLOT_BGCOLOR   = "rgba(0, 0, 0, 0.0)"
    PAPER_BGCOLOR  = "rgba(0, 0, 0, 0.0)"
    ANNOT_BGCOLOR  = "rgba(20, 20, 20, 1.0)"
    GRIDWIDTH      = 1.0
    ZEROLINEWIDTH  = 2.5
    TRACEWIDTH     = 2.5
    
    # some precalculated sizes
    XRANGE = [-PADDING_FACTOR * G_CFG.totalx, (1+PADDING_FACTOR) * G_CFG.totalx]
    YRANGE = [0, None]
    
    
    def _init_fig(G_CFG: GraphConfig):
        """ initialize the figure based on whether it needs to have suplots or not """
        
        if G_CFG.has_subplots is True:
            return make_subplots(specs=[[{"secondary_y": True}]])
        else:
            return go.Figure() 
      
    def _add_traces_main(G_CFG: GraphConfig, g_store: GraphStore, fig: go.Figure):
        """ loop through all the traces in the setup options dict for one graph and add the main traces """

        for trace_nr, trace_cfg in enumerate(G_CFG.traces):
            # create the trace
            trace = go.Scatter(
                x             = [None],
                y             = [None],
                name          = trace_cfg.name,
                mode          = "lines",
                line          = dict(
                    color     = trace_cfg.color,
                    width     = TRACEWIDTH,
                    shape     = trace_cfg.shape, 
                    smoothing = SMOOTHING,
                ),
                legendgroup   = f"group{trace_nr}",
                meta          = trace_cfg.name, # just to be able to include name in hovertemplate
                hovertemplate = "%{meta}: %{y:.4f}<extra></extra>", 
            )
        
            # add the trace to the primary or secondary subplot respectively
            if G_CFG.has_subplots is True: 
                fig.add_trace(trace, secondary_y=(False if trace_cfg.yaxis=="primary" else True))
            else:
                fig.add_trace(trace)
          
            # add an entry for the dict that matches a name to each plotly object number
            g_store.trc_t2id[trace_nr].register("main")

        return fig

    def _add_traces_min(G_CFG: GraphConfig, g_store: GraphStore, fig: go.Figure):
        
        if G_CFG.showmin is not False:            
            # if not false, showmin is expected to be the trace number for which the min is shown
            trace_nr_with_min  = int(G_CFG.showmin[-1]) # e.g. 1, extract from the traceX string
            
            # create the trace
            trace = go.Scatter(
                x          = [0, XRANGE[1]], # TODO: check if this is correct
                y          = [None, None], 
                mode       = "lines+markers",
                line       = dict(
                    color = G_CFG.traces[trace_nr_with_min].color,
                    width = TRACEWIDTH,
                    dash  = "dot",
                    shape = "linear",
                ),
                marker     = dict(
                    size       = [0, 20],
                    opacity    = [0, 1],
                    symbol     = ["circle", "triangle-left"], # TODO: use rotated shape?!
                    line_width = [0, 0]
                ),
                showlegend = False,
                hoverinfo  = "none",
            )
            
            # add the trace to the primary or secondary subplot respectively
            if G_CFG.has_subplots is True: 
                fig.add_trace(trace, secondary_y=(False if G_CFG.traces[trace_nr_with_min].yaxis=="primary" else True))
            else:
                fig.add_trace(trace)
            
            # add an entry for the dict that matches a name to each plotly object number
            g_store.trc_t2id[trace_nr_with_min].register("minline")
            
            # add the accompanying annotation (hidden until first data update!)
            fig.add_annotation(
                x       = XRANGE[1],
                y       = 0, # just a random number for invisible initialization
                xref    = "x",
                yref    = "y", # optional y2 should not be neccessary, subplots and showmin/max is exclusive!
                xanchor = "left",
                yanchor = "middle",
                text    = f"<b> minimum:<br> {0:07.4f}</b>", # same here, random init
                font      = dict(
                    family = "JetBrains Mono", 
                    size = 14, 
                    color = G_CFG.traces[trace_nr_with_min].color,
                ),
                showarrow = False,
                align     = "left",
                bgcolor   = ANNOT_BGCOLOR,
                visible   = False, # will be made visible with the first data update
            )
            
            
            # add an entry for the dict that matches a name to each plotly annotation number
            g_store.trc_a2id[trace_nr_with_min].register("minline")
            
        return fig
    
    def _add_traces_max(G_CFG: GraphConfig, g_store: GraphStore, fig: go.Figure):
        
        if G_CFG.showmax is not False:
            trace_nr_with_max  = int(G_CFG.showmax[-1]) # e.g. 1 extract from the traceX string
            
            # create the trace
            trace = go.Scatter(
                x          = [0, XRANGE[1]],
                y          = [None, None], 
                mode       = "lines+markers",
                line       = dict(
                    color = G_CFG.traces[trace_nr_with_max].color,
                    width = TRACEWIDTH,
                    dash  = "dot",
                    shape = "linear",
                ),
                marker     = dict(
                    size       = [0, 20],
                    opacity    = [0, 1],
                    symbol     = ["circle", "triangle-left"], # TODO: use rotated shape?!
                    line_width = [0, 0]
                ),
                showlegend = False,
                hoverinfo  = "none",
            )
            
            # add the trace to the primary or secondary subplot respectively
            if G_CFG.has_subplots is True: 
                fig.add_trace(trace, secondary_y=(False if G_CFG.traces[trace_nr_with_max].yaxis=="primary" else True))
            else:
                fig.add_trace(trace)
            
            # add an entry for the dict that matches a name to each trace number
            g_store.trc_t2id[trace_nr_with_max].register("maxline")
            
            # add the accompanying annotation (hidden until first data update!)
            fig.add_annotation(
                x       = XRANGE[1],
                y       = 0, # just a random number for invisible initialization
                xref    = "x",
                yref    = "y", # optional y2 should not be neccessary, subplots and showmin/max is exclusive!
                xanchor = "left",
                yanchor = "middle",
                text    = f"<b> maximum:<br> {0:07.4f}</b>", # same here, random init
                font      = dict(
                    family = "JetBrains Mono", 
                    size = 14, 
                    color = G_CFG.traces[trace_nr_with_max].color,
                ),
                showarrow = False,
                align     = "left",
                bgcolor   = ANNOT_BGCOLOR,
                visible   = False, # will be made visible with the first data update
            )
            
            # add an entry for the dict that matches a name to each plotly annotation number
            g_store.trc_a2id[trace_nr_with_max].register("maxline")
            
        return fig
    
    def _add_traces_error(G_CFG: GraphConfig, g_store: GraphStore, fig: go.Figure):
        
        for trace_nr, trace_cfg in enumerate(G_CFG.traces):
            if trace_cfg.errors is False:
                continue
            
            # create traces
            traceLo = go.Scatter(
                x           = [None],
                y           = [None],
                name        = f"{trace_cfg.name}_lo",
                mode        = "lines",
                line        = dict(
                    color     = trace_cfg.color,
                    width     = 0, 
                    shape     = trace_cfg.shape, 
                    smoothing = SMOOTHING
                ), 
                showlegend  = False,
                legendgroup = f"group{trace_nr}",
                hoverinfo   = "none",
            )     
            traceHi = go.Scatter(
                x           = [None],
                y           = [None],
                name        = f"{trace_cfg.name}_hi",
                mode        = "lines",
                line        = dict(
                    color     = trace_cfg.color, 
                    width     = 0, 
                    shape     = trace_cfg.shape, 
                    smoothing = SMOOTHING,
                ),
                fill        = "tonexty",
                fillcolor   = adjust_alpha(trace_cfg.color, 0.25),
                showlegend  = False,
                legendgroup = f"group{trace_nr}",
                hoverinfo   = "none",
            )
            traces = [traceLo, traceHi]
            
            # add the trace to the primary or secondary subplot respectively
            if G_CFG.has_subplots is True: 
                fig.add_traces(traces, secondary_ys=([False]*2 if trace_cfg.yaxis=="primary" else [True]*2))
            else:
                fig.add_traces(traces)
        
            # add an entry for the dict that matches a name to each trace number
            g_store.trc_t2id[trace_nr].register("lo")
            g_store.trc_t2id[trace_nr].register("hi")
        
        return fig
    
    def _add_traces_point(G_CFG: GraphConfig, g_store: GraphStore, fig: go.Figure):
        
        for trace_nr, trace_cfg in enumerate(G_CFG.traces):
            if trace_cfg.point is False:
                continue
            
            # create the endpoint trace
            trace = go.Scatter(
                x             = [None, None],
                y             = [None, None],
                mode          = "markers",
                marker        = dict(
                    color    = [adjust_alpha(trace_cfg.color, 0), trace_cfg.color], 
                    size     = [12, 5],
                    gradient = dict(
                        color = [adjust_alpha(trace_cfg.color, 0.5), trace_cfg.color], 
                        type  = ["radial", "radial"]
                    ),
                    opacity  = [1.0, 1.0],
                    line     = dict(width = [0, 0]),
                ),
                showlegend    = False,
                legendgroup   = f"group{trace_nr}",
                meta          = trace_cfg.name, # just to be able to include name in hovertemplate
                hovertemplate = "%{meta}: %{y:.4f}<extra></extra>", 
            )
        
            # add the trace to the primary or secondary subplot respectively
            if G_CFG.has_subplots is True: 
                fig.add_trace(trace, secondary_y=(False if trace_cfg.yaxis=="primary" else True))
            else:
                fig.add_trace(trace)
                
            # add an entry for the dict that matches a name to each plotly object number
            g_store.trc_t2id[trace_nr].register("point")
        
        return fig


    def _ud_layout(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_layout(
            uirevision    = "const", # i think this is to preserve zoom?
            margin        = dict(l=0, r=220, t=0, b=0),
            margin_pad    = 5,
            plot_bgcolor  = PLOT_BGCOLOR,
            paper_bgcolor = PAPER_BGCOLOR,
            legend        = dict(
                font    = dict( # setting font weight here will glitch legend visually!
                    color  = GRAY_LIGHT, 
                    family = "JetBrains Mono", 
                    size   = 12,
                ), 
                xref    = "container", 
                yref    = "container",
                xanchor = "right", 
                yanchor = "top",
                x       = 1.0, 
                y       = 1.0,
            ),
            hoverlabel    = dict(
                bgcolor     = "black",
                bordercolor = GRAY_LIGHT,
                font        = dict(
                    family = "JetBrains Mono", 
                    size   = 12, 
                    color  = GRAY_LIGHT
                ),
            ),
            hovermode     = "closest",
            modebar = {"orientation": "v"},
            shapes=[ # adds a vertical line at totalx
                dict(
                    type = "line",
                    x0   = G_CFG.totalx,
                    y0   = 0,
                    x1   = G_CFG.totalx,
                    y1   = 1,
                    xref = "x",
                    yref = "paper",
                    line = dict(
                        color = GRAY_DARK,
                        width = ZEROLINEWIDTH, 
                        dash  = "solid"
                    ),
                    layer="below" # places the shape behind traces
                ),
            ],
        ) 
        
        return fig
    
    def _ud_x_axis_general(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_xaxes(
            tickfont      = dict(
                family = "JetBrains Mono", 
                size   = 10, 
                color  = GRAY_LIGHT,
                weight = 500,
            ),
            zeroline      = True, 
            zerolinewidth = ZEROLINEWIDTH, 
            zerolinecolor = GRAY_DARK,
            showgrid      = True, 
            gridwidth     = GRIDWIDTH, 
            gridcolor     = GRAY_DARK, 
            griddash      = "dash",
            
            autorangeoptions_minallowed = XRANGE[0],
            autorangeoptions_maxallowed = XRANGE[1],
        )
        
        return fig
    
    def _ud_x_axis_subplots(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_xaxes(
            domain = [0, 1.0] # makes it so that subplots and normal plots take up the same amount of space
        )
        
        return fig
      
    def _ud_x_labl_general(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_xaxes(
            title          = G_CFG.xlabel,
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
            ),
        )
        
        return fig
    
    def _ud_y_axis_mono(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            tickfont       = dict(
                family = "JetBrains Mono", 
                size   = 10, 
                color  = GRAY_LIGHT,
                weight = 500,
            ), 
            tickangle      = -90, 
            zeroline       = True, 
            zerolinewidth  = ZEROLINEWIDTH, 
            zerolinecolor  = GRAY_DARK,
            showgrid       = True, 
            gridwidth      = GRIDWIDTH, 
            gridcolor      = GRAY_DARK,
            
            autorangeoptions_minallowed = YRANGE[0],
        )
        
        return fig
      
    def _ud_y_labl_mono(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            title          = G_CFG.ylabel1,
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
            ),
        )
        
        return fig
    
    def _ud_y_axis_primary(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            secondary_y   = False,
            
            tickfont      = dict(
                family = "JetBrains Mono", 
                size   = 10, 
                color  = GRAY_LIGHT,
                weight = 500,
                ), 
            tickangle     = -90, 
            zeroline      = True, 
            zerolinewidth = ZEROLINEWIDTH, 
            zerolinecolor = GRAY_DARK,
            showgrid      = True, 
            gridwidth     = GRIDWIDTH, 
            gridcolor     = GRAY_DARK,
            
            autorangeoptions_minallowed = YRANGE[0],
        )
        
        return fig
    
    def _ud_y_axis_secondary(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            secondary_y= True,
            
            tickfont      = dict(
                family = "JetBrains Mono", 
                size   = 10, 
                color  = GRAY_LIGHT,
                weight = 500,
                ), 
            tickangle     = -90, 
            zeroline      = False, 
            zerolinewidth = ZEROLINEWIDTH, 
            zerolinecolor = GRAY_DARK,
            showgrid      = False, 
            gridwidth     = GRIDWIDTH, 
            gridcolor     = GRAY_DARK,
            
            autorangeoptions_minallowed = YRANGE[0],
        )
        
        return fig
    
    def _ud_y_labl_primary(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            title          = G_CFG.ylabel1,
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
                ),
            secondary_y    = False,
        )
        
        return fig
    
    def _ud_y_labl_secondary(G_CFG: GraphConfig, fig: go.Figure):
        
        fig.update_yaxes(
            title          = G_CFG.ylabel2,
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
                ),
            secondary_y    = True,
        )
        
        return fig
    
    
    # ------------------------------------------------------------ create figure
    graph = _init_fig(G_CFG)
    # --------------------------------------------------------------- add traces
    #TODO: currently the ordering is done here, maybe use zordering?
    graph = _add_traces_error(G_CFG, g_store, graph)
    graph = _add_traces_main(G_CFG, g_store, graph)
    graph = _add_traces_min(G_CFG, g_store, graph)
    graph = _add_traces_max(G_CFG, g_store, graph)
    graph = _add_traces_point(G_CFG, g_store, graph)
    # -------------------------------------------------------- layouting general
    graph = _ud_layout(G_CFG, graph)
    # ------------------------------------------------------------- xaxis layout
    graph = _ud_x_axis_general(G_CFG, graph)
    if G_CFG.xlabel is not False:
        graph = _ud_x_labl_general(G_CFG, graph)
    if G_CFG.has_subplots is True:
        graph = _ud_x_axis_subplots(G_CFG, graph)
    # ------------------------------------------------------------- yaxis layout
    if G_CFG.has_subplots is True: 
        graph = _ud_y_axis_primary(G_CFG, graph)
        graph = _ud_y_axis_secondary(G_CFG, graph)
        if G_CFG.ylabel1 is not False:
            graph = _ud_y_labl_primary(G_CFG, graph)
        if G_CFG.ylabel2 is not False:
            graph = _ud_y_labl_secondary(G_CFG, graph)
    else:
        graph = _ud_y_axis_mono(G_CFG, graph)
        if G_CFG.ylabel1 is not False:
            graph = _ud_y_labl_mono(G_CFG, graph)
    
    return graph
