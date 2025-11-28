### IMPORTS ############################################################################################################
import numpy as np
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import plotly.graph_objects as go

from   mldashboard.utils import determine_single_range, determine_mixed_range, idx_next_smaller

from ...containers.setupconfig import Config, GraphConfig, TraceConfig
from ...containers.datastore import Store, GraphStore, TraceData, TraceT2Id, TraceA2Id, ProcsData

### DEFINITIONS ########################################################################################################

# TODO: also split this up into clean subfunctions, then the main workflow is more apparent
def callback_generate_flexgraph_patch(G_CFG: GraphConfig, g_store: GraphStore, g_chkp: list):


    # too keep track of wheter a range update is necessary, check if any min or max values have changed
    anyMinMaxChange = False
    
    # all possible changes are tracked with this patch. If no changes are made, the patch will just not change anything
    PTCH = Patch()
    
    # loop through each trace - updates --------------------------------------------------------------------------------
    for trace_nr, trace_cfg in enumerate(G_CFG.traces):
        # TODO: maybe make some handles for gstore.trc_data[trace_nr] xD
        # TODO: maybe also some handles for the registration
        
        # skip this trace, when it has no main data anyways (avoidy empty list issues down the line)
        if len(g_store.trc_data[trace_nr].x)==0 or len(g_store.trc_data[trace_nr].y)==0:
            continue
        
        # raw-data dependent updates -----------------------------------------------------------------------------------
        
        # main data update NO downsampling -------------------------------------
        if G_CFG.nxdown is False:
            # "freeze" the current length of the raw data store, so that it can handle having data appended to the store while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
            idx_raw_newest = min(len(g_store.trc_data[trace_nr].x), len(g_store.trc_data[trace_nr].y)) - 1
            
            old_chkp = g_chkp[trace_nr]
            new_chkp = idx_raw_newest 

            # only do data update if there is some new data
            if new_chkp > old_chkp:
                # -------------------------------------------- main trace update
                plotly_id = g_store.trc_t2id[trace_nr].main
                PTCH["data"][plotly_id]["x"].extend(g_store.trc_data[trace_nr].x[old_chkp+1:new_chkp+1])
                PTCH["data"][plotly_id]["y"].extend(g_store.trc_data[trace_nr].y[old_chkp+1:new_chkp+1])
                # ----------------------------------------------- endpoint trace 
                if G_CFG.traces[trace_nr].point is True:
                    plotly_id = g_store.trc_t2id[trace_nr].point
                    PTCH["data"][plotly_id]["x"] = [g_store.trc_data[trace_nr].x[new_chkp]]*2
                    PTCH["data"][plotly_id]["y"] = [g_store.trc_data[trace_nr].y[new_chkp]]*2
                # -------------------------------------------------- error trace     
                if G_CFG.traces[trace_nr].errors is True:
                    plotly_id = g_store.trc_t2id[trace_nr].lo
                    PTCH["data"][plotly_id]["x"].extend(g_store.trc_data[trace_nr].x[old_chkp+1:new_chkp+1])
                    PTCH["data"][plotly_id]["y"].extend(g_store.trc_data[trace_nr].ylo[old_chkp+1:new_chkp+1])
                    plotly_id = g_store.trc_t2id[trace_nr].hi
                    PTCH["data"][plotly_id]["x"].extend(g_store.trc_data[trace_nr].x[old_chkp+1:new_chkp+1])
                    PTCH["data"][plotly_id]["y"].extend(g_store.trc_data[trace_nr].yhi[old_chkp+1:new_chkp+1])
                
                g_chkp[trace_nr] = new_chkp
    
        # main data update WITH downsampling -----------------------------------
        if G_CFG.nxdown is not False:
            # TODO: idx names are a bit weird here? 
            # "freeze" the current length of the raw data store, so that it can handle having data appended to the store while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
            idx_raw_newest = min(len(g_store.trc_data[trace_nr].x), len(g_store.trc_data[trace_nr].y)) - 1
            
            # determine the potential new checkpoint: finds the index of the next smaller element (to latest raw x) in the downsampled x "grid". this will be the latest downsampled point that is fully covered by raw data.
            old_chkp = g_chkp[trace_nr]
            new_chkp = idx_next_smaller(
                g_store.trc_data[trace_nr].xdown, 
                g_store.trc_data[trace_nr].x[idx_raw_newest]
            )

            # only do data update and downsample if there is enough new data to cover a new xDown point
            if new_chkp > old_chkp:
                
                # find the lower end of the raw data that actually needs to be sampled. (just needs to fully cover the x downsampled interval from old_chkp to new_chkp, anything else is redundant)
                idx_raw_oldest = idx_next_smaller(
                    g_store.trc_data[trace_nr].x, 
                    g_store.trc_data[trace_nr].xdown[old_chkp+1]
                )
                
                # -------------------------------------------- main trace update
                yDown = np.interp(
                    g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1],
                    g_store.trc_data[trace_nr].x[idx_raw_oldest:idx_raw_newest+1],
                    g_store.trc_data[trace_nr].y[idx_raw_oldest:idx_raw_newest+1],
                )
                plotly_id = g_store.trc_t2id[trace_nr].main
                PTCH["data"][plotly_id]["x"].extend(list(g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1]))
                PTCH["data"][plotly_id]["y"].extend(list(yDown))
                
                # ----------------------------------------------- endpoint trace 
                if G_CFG.traces[trace_nr].point is True:
                    plotly_id = g_store.trc_t2id[trace_nr].point
                    PTCH["data"][plotly_id]["x"] = [g_store.trc_data[trace_nr].xdown[new_chkp]]*2
 
                # -------------------------------------------------- error trace 
                if G_CFG.traces[trace_nr].errors is True:
                    yLoDown = np.interp(
                        g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1],
                        g_store.trc_data[trace_nr].x[idx_raw_oldest:idx_raw_newest+1],
                        g_store.trc_data[trace_nr].ylo[idx_raw_oldest:idx_raw_newest+1],
                    ) 
                    plotly_id = g_store.trc_t2id[trace_nr].lo
                    PTCH["data"][plotly_id]["x"].extend(list(g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1]))
                    PTCH["data"][plotly_id]["y"].extend(list(yLoDown))
                    
                    
                    yHiDown = np.interp(
                        g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1],
                        g_store.trc_data[trace_nr].x[idx_raw_oldest:idx_raw_newest+1],
                        g_store.trc_data[trace_nr].yhi[idx_raw_oldest:idx_raw_newest+1],
                    ) 
                    plotly_id = g_store.trc_t2id[trace_nr].hi
                    PTCH["data"][plotly_id]["x"].extend(list(g_store.trc_data[trace_nr].xdown[old_chkp+1:new_chkp+1]))
                    PTCH["data"][plotly_id]["y"].extend(list(yHiDown))

                g_chkp[trace_nr] = new_chkp
         
        # min/max dependent line updated -------------------------------------------------------------------------------
        
        # already check if min / max has changed and reset flag to avoid missing updates. 
        hasNewMin = False
        hasNewMax = False
        if g_store.trc_data[trace_nr].ynewmin is True:
            hasNewMin       = True
            anyMinMaxChange = True
            g_store.trc_data[trace_nr].ynewmin = False
            
        if g_store.trc_data[trace_nr].ynewmax is True:
            hasNewMax       = True
            anyMinMaxChange = True
            g_store.trc_data[trace_nr].ynewmax = False
            
        # ------------------------------------------------- update showmin trace
        if (G_CFG.showmin==trace_nr) and (hasNewMin is True):
            plotly_id = g_store.trc_t2id[trace_nr].minline
            newMin = g_store.trc_data[trace_nr].ymin
            PTCH["data"][plotly_id]["y"] = [newMin]*2 # x coords always stay at either ends of the graph ...
            
            # also update the according annotation, make it visible (only as an effect once)
            plotly_id = g_store.trc_a2id[trace_nr].minline
            PTCH["layout"]["annotations"][plotly_id]["text"] = f"<b> minimum:<br> {newMin:07.4f}</b>"
            PTCH["layout"]["annotations"][plotly_id]["y"] = newMin
            PTCH["layout"]["annotations"][plotly_id]["visible"] = True
            
        
        # ------------------------------------------------- update showmax trace
        if (G_CFG.showmax==trace_nr) and (hasNewMax is True):    
            plotly_id = g_store.trc_t2id[trace_nr].maxline
            newMax = g_store.trc_data[trace_nr].ymax
            PTCH["data"][plotly_id]["y"] = [newMax]*2
            
            # also update the according annotation, make it visible (only as an effect once)
            plotly_id = g_store.trc_a2id[trace_nr].maxline
            PTCH["layout"]["annotations"][plotly_id]["text"] = f"<b> maximum:<br> {newMax:07.4f}</b>"
            PTCH["layout"]["annotations"][plotly_id]["y"] = newMax
            PTCH["layout"]["annotations"][plotly_id]["visible"] = True

    # min/max dependent autorange updates ------------------------------------------------------------------------------
    
    # normal Figure ------------------------------------------------------------
    if (anyMinMaxChange is True) and (G_CFG.has_subplots is False):
        # gather all mins / maxes and take the min / max over all of them (with a ceil / floor of 0)
        MIN = min([g_store.trc_data[t_nr].ymin for t_nr, _ in enumerate(G_CFG.traces)] + [0])
        MAX = max([g_store.trc_data[t_nr].ymax for t_nr, _ in enumerate(G_CFG.traces)] + [0])
        
        # ----------------------------------------------------- update autorange
        yRng = determine_single_range(MIN, MAX, factor=0.1)
        PTCH["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = yRng[0]
        PTCH["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = yRng[1]
    
    # subplot Figure -----------------------------------------------------------        
    if (anyMinMaxChange is True) and (G_CFG.has_subplots is True):
        # gather all mins / maxes but separate for primary and secondary plot
        MIN1 = min(
            [g_store.trc_data[t_nr].ymin if t_cfg.yaxis=="primary" else 0 for t_nr, t_cfg in enumerate(G_CFG.traces)] 
            + [0]
        )
        MAX1 = max(
            [g_store.trc_data[t_nr].ymax if t_cfg.yaxis=="primary" else 0 for t_nr, t_cfg in enumerate(G_CFG.traces)] 
            + [0]
        )
        MIN2 = min(
            [g_store.trc_data[t_nr].ymin if t_cfg.yaxis=="secondary" else 0 for t_nr, t_cfg in enumerate(G_CFG.traces)] 
            + [0]
        )
        MAX2 = max(
            [g_store.trc_data[t_nr].ymax if t_cfg.yaxis=="secondary" else 0 for t_nr, t_cfg in enumerate(G_CFG.traces)] 
            + [0]
        )
        
        # ----------------------------------------------------- update autorange
        # TODO: route factor out
        yRng1        = determine_single_range(MIN1, MAX1, factor=0.1)
        yRng2        = determine_single_range(MIN2, MAX2, factor=0.1)
        yRng1, yRng2 = determine_mixed_range(yRng1, yRng2)
        PTCH["layout"]["yaxis"]["autorangeoptions"]["minallowed"]  = yRng1[0]
        PTCH["layout"]["yaxis"]["autorangeoptions"]["maxallowed"]  = yRng1[1]
        PTCH["layout"]["yaxis2"]["autorangeoptions"]["minallowed"] = yRng2[0]
        PTCH["layout"]["yaxis2"]["autorangeoptions"]["maxallowed"] = yRng2[1]


    # print(PTCH.to_plotly_json())
    PTCH = Patch()
    
    PTCH["data"][0]["x"].extend([0.5])
    PTCH["data"][0]["y"].extend([0.5])
    
    return PTCH, g_chkp

def callback_update_proc_speed(store: Store):
    proc_speed = store.procs.speed # as deque, last few speeds
    
    if len(proc_speed) == 0:
        return [f"---'---.-- samples/sec"]
    
    avg_speed = sum(proc_speed) / len(proc_speed)
    return [f"{avg_speed:,.2f} samples/sec".replace(",", "'")]

