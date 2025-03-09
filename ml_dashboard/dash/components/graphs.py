import numpy as np
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   ml_dashboard.utils import adjust_alpha


def make_flexgraph(setup_options: dict, store: dict, n2t: dict, graphnr: int):
    # some global customization params. TODO: make nicely controllable globally
    padding_factor = 0.03 # the additional space that is added + and - along the x axis
    smoothing      = 0.60 # smooting factor of all the spline traces
    GRAY_LIGHT     = "rgb(200, 200, 200)"
    GRAY_DARK      = "rgb(80, 80, 80)"
    PLOT_BGCOLOR   = "rgba(0, 0, 0, 0.0)"
    PAPER_BGCOLOR  = "rgba(0, 0, 0, 0.0)"
    ANNOT_BGCOLOR  = "rgba(20, 20, 20, 1.0)"
    GRIDWIDTH      = 1.0
    ZEROLINEWIDTH  = 2.5
    TRACEWIDTH     = 2.5
    
    # some handles for often used vars
    opt = setup_options[f"graph{graphnr}"]["options"]
    trc = setup_options[f"graph{graphnr}"]["traces"]
    
    # some precalculated sizes
    totalx = opt["totalx"] # total number of Samples to be processed. defines x range
    xrange = [-padding_factor * totalx, (1+padding_factor) * totalx]
    yrange = [0, None]
    
    def _init_fig(opt: dict, trc: dict):
        """ initialize the figure based on whether it needs to have suplots or not """
        
        if opt["subplots"] is True:
            return make_subplots(specs=[[{"secondary_y": True}]])
        else:
            return go.Figure() 
        
    def _add_traces_main(opt: dict, trc: dict, fig: go.Figure):
        """ loop through all the traces in the setup options dict for one graph and add the main traces """

        for keyT in trc.keys():
            t = int(keyT[-1]) # retrieve trace number at the end of keyname (traceX)
            
            # create the trace
            trace = go.Scatter(
                x             = [None],
                y             = [None],
                name          = trc[keyT]["N"],
                mode          = "lines",
                line          = dict(
                    color     = trc[keyT]["C"],
                    width     = TRACEWIDTH,
                    shape     = trc[keyT]["S"], 
                    smoothing = smoothing,
                ),
                legendgroup   = f"group{t}",
                meta          = trc[keyT]["N"], # just to be able to include name in hovertemplate
                hovertemplate = "%{meta}: %{y:.4f}<extra></extra>", 
            )

            # add the trace to the primary or secondary subplot respectively
            if opt["subplots"] is True: 
                fig.add_trace(trace, secondary_y = (False if trc[keyT]["T"] == "primary" else True))
            else:
                fig.add_trace(trace)
                
            # add an entry for the dict that matches a name to each trace number
            n2t[f"g{graphnr}"][f"t{t}_main"] = len(n2t[f"g{graphnr}"])
        return fig
    
    def _add_traces_min(opt: dict, trc: dict, fig: go.Figure):
        if opt["showmin"] is not False:
            trace_w_min_key = opt["showmin"]            # e.g. trace1
            trace_w_min_nr  = int(trace_w_min_key[-1]) # e.g. 1
            
            # create the trace
            trace = go.Scatter(
                x          = [0, xrange[1]], # TODO: check if this is coorect
                y          = [None, None], 
                mode       = "lines+markers",
                line       = dict(
                    color = trc[trace_w_min_key]["C"],
                    width = TRACEWIDTH,
                    dash  = "dot",
                    shape = "linear",
                ),
                marker     = dict(
                    size       = [0, 20],
                    opacity    = [0, 1],
                    symbol     = ["circle", "triangle-left"], 
                    line_width = [0, 0]
                ),
                showlegend = False,
                hoverinfo  = "none",
            )
            
            # add the trace to the primary or secondary subplot respectively
            if opt["subplots"] is True: 
                fig.add_trace(trace, secondary_y = (False if trc[trace_w_min_key]["T"] == "primary" else True))
            else:
                fig.add_trace(trace)
            
            # add an entry for the dict that matches a name to each trace number
            n2t[f"g{graphnr}"][f"t{trace_w_min_nr}_minline"] = len(n2t[f"g{graphnr}"])
            
            # add the accompanying annotation (hidden until first data update!)
            fig.update_layout(
                annotations = [
                    dict(
                        x       = xrange[1],
                        y       = 0, # just a random number for invisible initialization
                        xref    = "x",
                        yref    = "y", # optional y2 should not be neccessary, subplots and showmin/max is exclusive!
                        xanchor = "left",
                        yanchor = "middle",
                        text    = f"<b> minimum:<br> {0:07.4f}</b>", # same here, random init
                        font      = dict(
                            family = "JetBrains Mono", 
                            size = 14, 
                            color = trc[trace_w_min_key]["C"],
                        ),
                        showarrow = False,
                        align     = "left",
                        bgcolor   = ANNOT_BGCOLOR,
                        visible   = False, # will be made visible with the first data update
                    )
                ]
            )
            
            
        return fig
    
    def _add_traces_max(opt: dict, trc: dict, fig: go.Figure):
        if opt["showmax"] is not False:
            trace_w_max_key = opt["showmax"]            # e.g. trace1
            trace_w_max_nr  = int(trace_w_max_key[-1]) # e.g. 1
            
            # create the trace
            trace = go.Scatter(
                x          = [0, xrange[1]],
                y          = [None, None], 
                mode       = "lines+markers",
                line       = dict(
                    color = trc[trace_w_max_key]["C"],
                    width = TRACEWIDTH,
                    dash  = "dot",
                    shape = "linear",
                ),
                marker     = dict(
                    size       = [0, 20],
                    opacity    = [0, 1],
                    symbol     = ["circle", "triangle-left"], 
                    line_width = [0, 0]
                ),
                showlegend = False,
                hoverinfo  = "none",
            )
            
            # add the trace to the primary or secondary subplot respectively
            if opt["subplots"] is True: 
                fig.add_trace(trace, secondary_y = (False if trc[trace_w_max_key]["T"] == "primary" else True))
            else:
                fig.add_trace(trace)
            
            # add an entry for the dict that matches a name to each trace number
            n2t[f"g{graphnr}"][f"t{trace_w_max_nr}_maxline"] = len(n2t[f"g{graphnr}"])
            
            # add the accompanying annotation (hidden until first data update!)
            fig.update_layout(
                annotations = [
                    dict(
                        x       = xrange[1],
                        y       = 0, # just a random number for invisible initialization
                        xref    = "x",
                        yref    = "y", # optional y2 should not be neccessary, subplots and showmin/max is exclusive!
                        xanchor = "left",
                        yanchor = "middle",
                        text    = f"<b> maximum:<br> {0:07.4f}</b>", # same here, random init
                        font      = dict(
                            family = "JetBrains Mono", 
                            size = 14, 
                            color = trc[trace_w_max_key]["C"],
                        ),
                        showarrow = False,
                        align     = "left",
                        bgcolor   = ANNOT_BGCOLOR,
                        visible   = False, # will be made visible with the first data update
                    )
                ]
            )
            
        return fig
    
    def _add_traces_error(opt: dict, trc: dict, fig: go.Figure):
        
        for keyT in trc.keys():
            if trc[keyT]["E"] is False:
                continue
            
            t = int(keyT[-1]) # retrieve trace number at the end of keyname (traceX)
            
            # create traces
            traceLo = go.Scatter(
                x           = [None],
                y           = [None],
                name        = f"{trc[keyT]["N"]}_lo",
                mode        = "lines",
                line        = dict(
                    color     = trc[keyT]["C"],
                    width     = 0, 
                    shape     = trc[keyT]["S"], 
                    smoothing = smoothing
                ), 
                showlegend  = False,
                legendgroup = f"group{t}",
                hoverinfo   = "none",
            )
            traceHi = go.Scatter(
                x           = [None],
                y           = [None],
                name        = f"{trc[keyT]["N"]}_hi",
                mode        = "lines",
                line        = dict(
                    color     = trc[keyT]["C"], 
                    width     = 0, 
                    shape     = trc[keyT]["S"], 
                    smoothing = smoothing,
                ),
                fill        = "tonexty",
                fillcolor   = adjust_alpha(trc[keyT]["C"], 0.25),
                showlegend  = False,
                legendgroup = f"group{t}",
                hoverinfo   = "none",
            )
            traces = [traceLo, traceHi]
            
            # add the trace to the primary or secondary subplot respectively
            if opt["subplots"] is True:
                fig.add_traces(traces, secondary_ys = ([False]*2 if trc[keyT]["T"] == "primary" else [True]*2))
            else:
                fig.add_traces(traces)
                
            # add an entry for the dict that matches a name to each trace number
            n2t[f"g{graphnr}"][f"t{t}_lo"] = len(n2t[f"g{graphnr}"])
            n2t[f"g{graphnr}"][f"t{t}_hi"] = len(n2t[f"g{graphnr}"])
        return fig
    
    def _add_traces_point(opt: dict, trc: dict, fig: go.Figure):
        
        for keyT in trc.keys():
            if trc[keyT]["P"] is False:
                continue
            
            t = int(keyT[-1])
            
            # create the trace
            trace = go.Scatter(
                x             = [None, None],
                y             = [None, None],
                mode          = "markers",
                marker        = dict(
                    color    = [adjust_alpha(trc[keyT]["C"], 0), trc[keyT]["C"]], 
                    size     = [12, 5],
                    gradient = dict(
                        color = [adjust_alpha(trc[keyT]["C"], 0.5), trc[keyT]["C"]], 
                        type  = ["radial", "radial"]
                    ),
                    opacity  = [1.0, 1.0],
                    line     = dict(width = [0, 0]),
                ),
                showlegend    = False,
                legendgroup   = f"group{t}",
                meta          = trc[keyT]["N"], # just to be able to include name in hovertemplate
                hovertemplate = "%{meta}: %{y:.4f}<extra></extra>", 
            )
            
            # add the trace to the primary or secondary subplot respectively
            if opt["subplots"] is True:
                fig.add_trace(trace, secondary_y = (False if trc[keyT]["T"] == "primary" else True))
            else:
                fig.add_trace(trace)
        
            # add an entry for the dict that matches a name to each trace number
            n2t[f"g{graphnr}"][f"t{t}_point"] = len(n2t[f"g{graphnr}"])
        return fig
    
    def _ud_layout(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_layout(
            uirevision    = "const",
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
                    x0   = totalx,
                    y0   = 0,
                    x1   = totalx,
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
    
    def _ud_x_axis_general(opt: dict, trc: dict, fig: go.Figure):
        
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
            
            autorangeoptions_minallowed = xrange[0],
            autorangeoptions_maxallowed = xrange[1],
        )
        
        return fig
    
    def _ud_x_axis_subplots(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_xaxes(
            domain = [0, 1.0] # makes it so that subplots and normal plots take up the same amount of space
        )
        
        return fig
      
    def _ud_x_labl_general(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_xaxes(
            title          = opt["xlabel"],
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
            ),
        )
        
        return fig
    
    def _ud_y_axis_mono(opt: dict, trc: dict, fig: go.Figure):
        
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
            
            autorangeoptions_minallowed = yrange[0],
        )
        
        return fig
      
    def _ud_y_labl_mono(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_yaxes(
            title          = opt["ylabel1"],
            title_standoff = 15,
            title_font     = dict(
                color  = GRAY_LIGHT,
                family = "JetBrains Mono",
                size   = 14,
                weight = 500,
            ),
        )
        
        return fig
    
    def _ud_y_axis_primary(opt: dict, trc: dict, fig: go.Figure):
        
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
            
            autorangeoptions_minallowed = yrange[0],
        )
        
        return fig
    
    def _ud_y_axis_secondary(opt: dict, trc: dict, fig: go.Figure):
        
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
            
            autorangeoptions_minallowed = yrange[0],
        )
        
        return fig
    
    def _ud_y_labl_primary(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_yaxes(
            title          = opt["ylabel1"],
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
    
    def _ud_y_labl_secondary(opt: dict, trc: dict, fig: go.Figure):
        
        fig.update_yaxes(
            title          = opt["ylabel2"],
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
    graph = _init_fig(opt, trc)
    # --------------------------------------------------------------- add traces
    graph = _add_traces_error(opt, trc, graph)
    graph = _add_traces_main(opt, trc, graph)
    graph = _add_traces_min(opt, trc, graph)
    graph = _add_traces_max(opt, trc, graph)
    graph = _add_traces_point(opt, trc, graph)
    # -------------------------------------------------------- layouting general
    graph = _ud_layout(opt, trc, graph)
    # ------------------------------------------------------------- xaxis layout
    graph = _ud_x_axis_general(opt, trc, graph)
    if opt["xlabel"] is not False:
        graph = _ud_x_labl_general(opt, trc, graph)
    if opt["subplots"] is True:
        graph = _ud_x_axis_subplots(opt, trc, graph)
    # ------------------------------------------------------------- yaxis layout
    if opt["subplots"] is True: 
        graph = _ud_y_axis_primary(opt, trc, graph)
        graph = _ud_y_axis_secondary(opt, trc, graph)
        if opt["ylabel1"] is not False:
            fig = _ud_y_labl_primary(opt, trc, graph)
        if opt["ylabel2"] is not False:
            fig = _ud_y_labl_secondary(opt, trc, graph)
    else:
        graph = _ud_y_axis_mono(opt, trc, graph)
        if opt["ylabel1"] is not False:
            fig = _ud_y_labl_mono(opt, trc, graph)
    
    return fig

