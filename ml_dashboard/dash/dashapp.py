### IMPORTS ############################################################################################################
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ml_dashboard.dash.components import make_graphcard
from ml_dashboard.dash.components import make_flexgraph
from ml_dashboard.utils           import determine_single_range, determine_mixed_range


import time
def perf_timer(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()
        print(f"callback execution took: {(t1-t0)*1000:.4f}ms")
        return result
    return wrapper

def make_plotter_app(setup_options: dict, store: dict, n2t: dict):
    
    # declare variable and handles -------------------------------------------------------------------------------------
    app = Dash(
        __name__,
        external_stylesheets = [],
        assets_folder        = "./assets" # specify assets folder because project structure is different from default
    )
    
    graph1 = make_flexgraph(setup_options, store, n2t, graphnr=1)
    graph2 = make_flexgraph(setup_options, store, n2t, graphnr=2)
    graph3 = make_flexgraph(setup_options, store, n2t, graphnr=3)

    # initialize a checkpoint dict to -1 for each trace to pass to the dcc.stores (temporary)
    chkpts = []
    for graphXdict in setup_options.values():
        chkpts.append({f"t{int(keyT[-1])}": -1 for keyT in graphXdict["traces"].keys()})
    
    # app layout -------------------------------------------------------------------------------------------------------
    app.layout = html.Div(
        className = "main-grid",
        children = [
            make_graphcard(title = "title A", gridbox = "A", graphid = "graph1", graphfig = graph1),
            make_graphcard(title = "title B", gridbox = "B", graphid = "graph2", graphfig = graph2),
            make_graphcard(title = "title C", gridbox = "C", graphid = "graph3", graphfig = graph3),
            html.Div(
                className = "card main-grid-boxD",
                children  = [
                    html.Div(className = "header", children = ["title card D"]),
                    html.Div(className = "body",   children = ["somebodytext"]),
                ],
            ),
            html.Div(
                className = "card main-grid-boxE",
                children  = [
                    html.Div(className = "header", children = ["title card E"]),
                    html.Div(className = "body",   children = ["somebodytext"]),
                ],
            ),
            
            dcc.Interval(
                id          = "ud-interval-1",
                interval    = 1000,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud-interval-2",
                interval    = 1000,
                n_intervals = 0,
            ),
            dcc.Interval(
                id          = "ud-interval-3",
                interval    = 1000,
                n_intervals = 0,
            ),
            
            # TODO: initialize with actual dict and -1 for each t
            dcc.Store(id="chkp-graph-1", data=chkpts[0]),
            dcc.Store(id="chkp-graph-2", data=chkpts[1]),
            dcc.Store(id="chkp-graph-3", data=chkpts[2]),
        ]
    )
    
    # callbacks --------------------------------------------------------------------------------------------------------
    @app.callback(
        [Output("graph1", "figure"), Output("chkp-graph-1", "data")],
        [Input("ud-interval-1", "n_intervals")],
        [State("chkp-graph-1", "data")]
    )
    def update_graph_1(n, chkp_dict):
        
        opt = setup_options["graph1"]["options"]
        trc = setup_options["graph1"]["traces"]
        
        DO_DOWNSAMPLE   = False
        
        anyMinMaxChange = False
        
        ptch = Patch()
        
        # loop through all the traces and apply all possible updates to each
        for keyT in trc.keys():
            t = int(keyT[-1])
            
            # skip this trace, when it has no main data anyways (avoidy empty list issues down the line)
            if (len(store[f"g1"][f"t{t}_x"])) == 0 or (len(store[f"g1"][f"t{t}_y"]) == 0):
                continue 
            
            # data dependent stuff =============================================
            
            # main data update without downsampling
            if DO_DOWNSAMPLE is False:
                # freeze the current length of the raw data store, so that it can handle having data appended to the store while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
                idx_raw_newest = min(len(store[f"g1"][f"t{t}_x"]), len(store[f"g1"][f"t{t}_y"])) -1
                
                old_chkp = chkp_dict[f"t{t}"]
                new_chkp = idx_raw_newest
                
                # only do data update if there is some new data
                if new_chkp > old_chkp:
                    # main trace update ----------------------------------------
                    n2t_nr = n2t[f"g1"][f"t{t}_main"]
                    ptch["data"][n2t_nr]["x"].extend(store[f"g1"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                    ptch["data"][n2t_nr]["y"].extend(store[f"g1"][f"t{t}_y"][old_chkp+1:new_chkp+1])
                    
                    # endpoint trace -------------------------------------------
                    if trc[keyT]["P"] is True:
                        n2t_nr = n2t[f"g1"][f"t{t}_point"]
                        ptch["data"][n2t_nr]["x"] = [store[f"g1"][f"t{t}_x"][new_chkp]]
                        ptch["data"][n2t_nr]["y"] = [store[f"g1"][f"t{t}_y"][new_chkp]]
                    
                    # error trace ----------------------------------------------    
                    if trc[keyT]["E"] is True:
                        n2t_nr = n2t[f"g1"][f"t{t}_lo"]
                        ptch["data"][n2t_nr]["x"].extend(store[f"g1"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                        ptch["data"][n2t_nr]["y"].extend(store[f"g1"][f"t{t}_yLo"][old_chkp+1:new_chkp+1])
                        n2t_nr = n2t[f"g1"][f"t{t}_hi"]
                        ptch["data"][n2t_nr]["x"].extend(store[f"g1"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                        ptch["data"][n2t_nr]["y"].extend(store[f"g1"][f"t{t}_yHi"][old_chkp+1:new_chkp+1])
                    
                    chkp_dict[f"t{t}"] = new_chkp
                
            # main data update with downsampling
            if DO_DOWNSAMPLE is True:
                ... 
              
            # min max lines  ===================================================
            
            # already check if min / max has changed and reset flag to avoid missing updates. 
            hasNewMin = False
            hasNewMax = False
            if store[f"g1"][f"t{t}_yMinNew"] is True:
                hasNewMin       = True
                anyMinMaxChange = True
                store[f"g1"][f"t{t}_yMinNew"] = False
                
            if store[f"g1"][f"t{t}_yMaxNew"] is True:
                hasNewMax       = True
                anyMinMaxChange = True
                store[f"g1"][f"t{t}_yMaxNew"] = False
                
            # update showmin trace
            if (opt["showmin"] == keyT) and (hasNewMin is True):                 
                n2t_nr = n2t[f"g1"][f"t{t}_minline"]
                newMin = store[f"g1"][f"t{t}_yMin"]
                
                ptch["data"][n2t_nr]["y"] = [newMin]*2
                
                ptch["layout"]["annotations"][0]["text"] = f"<b> minimum:<br> {newMin:07.4f}</b>"
                ptch["layout"]["annotations"][0]["y"] = newMin
                ptch["layout"]["annotations"][0]["visible"] = True
            
            # update showmax trace
            if (opt["showmax"] == keyT) and (hasNewMax is True):    
                n2t_nr = n2t[f"g1"][f"t{t}_maxline"]
                newMax = store[f"g1"][f"t{t}_yMax"]
                
                ptch["data"][n2t_nr]["y"] = [newMax]*2
        
                ptch["layout"]["annotations"][0]["text"] = f"<b> maximum:<br> {newMax:07.4f}</b>"
                ptch["layout"]["annotations"][0]["y"] = newMax
                ptch["layout"]["annotations"][0]["visible"] = True
        
        # min max range ========================================================

        # adjust range
        if (anyMinMaxChange is True) and (opt["subplots"] is False):

            # gather all mins / maxes and take the min / max over all of them (with a ceil / floor of 0)
            MIN = min([store[f"g1"][f"t{int(keyT[-1])}_yMin"] for keyT in trc.keys()] + [0])
            MAX = max([store[f"g1"][f"t{int(keyT[-1])}_yMax"] for keyT in trc.keys()] + [0])

            yRng = determine_single_range(MAX, MIN, factor=0.1)
            
            ptch["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = yRng[0]
            ptch["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = yRng[1]
                
        if (anyMinMaxChange is True) and (opt["subplots"] is True):
            
            # gather all mins / maxes but separate for primary and secondary plot
            min1_coll = [0]
            max1_coll = [0]
            min2_coll = [0]
            max2_coll = [0]
            
            for keyT in trc.keys():
                t = int(keyT[-1])
                
                if trc[keyT]["T"] == "primary":
                    min1_coll.append(store[f"g1"][f"t{t}_yMin"])
                    max1_coll.append(store[f"g1"][f"t{t}_yMax"])
                if trc[keyT]["T"] == "secondary":
                    min2_coll.append(store[f"g1"][f"t{t}_yMin"])
                    max2_coll.append(store[f"g1"][f"t{t}_yMax"])
            
            [store[f"g1"][f"t{int(keyT[-1])}_yMin"] if trc[keyT]["T"] == "primary" else 0 for keyT in trc.keys()] + [0]
            
            
            
            MIN1 = min(min1_coll)
            MAX1 = max(max1_coll)
            MIN2 = min(min2_coll)
            MAX2 = max(max2_coll)
            
            yRng1 = determine_single_range(MIN1, MAX1, factor=0.1)
            yRng2 = determine_single_range(MIN2, MAX2, factor=0.1)
            
            yRng1, yRng2 = determine_mixed_range(yRng1, yRng2)
            
            ptch["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = yRng1[0]
            ptch["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = yRng1[1]
 
            ptch["layout"]["yaxis2"]["autorangeoptions"]["minallowed"] = yRng2[0]
            ptch["layout"]["yaxis2"]["autorangeoptions"]["maxallowed"] = yRng2[1]

            
            

        
        return ptch, chkp_dict
    
    
    return app