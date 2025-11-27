### IMPORTS ############################################################################################################
import numpy as np
from   dash import Dash, Input, Output, State, Patch, dcc, html, no_update
import plotly.graph_objects as go
from   mldashboard.utils import determine_single_range, determine_mixed_range, idx_next_smaller


### DEFINITIONS ########################################################################################################
def callback_generate_flexgraph_patch(setup_options: dict, store: dict, n2t: dict, chkp_traces: dict, graphnr: int):
    # some useful handles
    g   = graphnr
    opt = setup_options[f"graph{g}"]["options"]
    trc = setup_options[f"graph{g}"]["traces"]

    # too keep track of wheter a range update is necessary, check if any min or max values have changed
    anyMinMaxChange = False
    
    # all possible changes are tracked with the patch. If no changes are made, the patch will just not change anything
    PTCH = Patch()
    
    # ------------------------------------------------------------------------------------------------------------------
    for keyT in trc.keys():
        t = int(keyT[-1])
        
        # skip this trace, when it has no main data anyways (avoidy empty list issues down the line)
        if (len(store[f"g{g}"][f"t{t}_x"])) == 0 or (len(store[f"g{g}"][f"t{t}_y"]) == 0):
            continue 
        
        # raw-data dependent updates -----------------------------------------------------------------------------------
        
        # main data update NO downsampling -------------------------------------
        if opt["downsamplex"] is False:
            # freeze the current length of the raw data store, so that it can handle having data appended to the store while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
            idx_raw_newest = min(len(store[f"g{g}"][f"t{t}_x"]), len(store[f"g{g}"][f"t{t}_y"])) -1
            
            old_chkp = chkp_traces[f"t{t}"]
            new_chkp = idx_raw_newest
            
            # only do data update if there is some new data
            if new_chkp > old_chkp:
                # -------------------------------------------- main trace update
                n2t_nr = n2t[f"g{g}"][f"t{t}_main"]
                PTCH["data"][n2t_nr]["x"].extend(store[f"g{g}"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                PTCH["data"][n2t_nr]["y"].extend(store[f"g{g}"][f"t{t}_y"][old_chkp+1:new_chkp+1])
                
                # ----------------------------------------------- endpoint trace 
                if trc[keyT]["P"] is True:
                    n2t_nr = n2t[f"g{g}"][f"t{t}_point"]
                    PTCH["data"][n2t_nr]["x"] = [store[f"g{g}"][f"t{t}_x"][new_chkp]]*2
                    PTCH["data"][n2t_nr]["y"] = [store[f"g{g}"][f"t{t}_y"][new_chkp]]*2
                
                # -------------------------------------------------- error trace     
                if trc[keyT]["E"] is True:
                    n2t_nr = n2t[f"g{g}"][f"t{t}_lo"]
                    PTCH["data"][n2t_nr]["x"].extend(store[f"g{g}"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                    PTCH["data"][n2t_nr]["y"].extend(store[f"g{g}"][f"t{t}_yLo"][old_chkp+1:new_chkp+1])
                    n2t_nr = n2t[f"g{g}"][f"t{t}_hi"]
                    PTCH["data"][n2t_nr]["x"].extend(store[f"g{g}"][f"t{t}_x"][old_chkp+1:new_chkp+1])
                    PTCH["data"][n2t_nr]["y"].extend(store[f"g{g}"][f"t{t}_yHi"][old_chkp+1:new_chkp+1])
                
                chkp_traces[f"t{t}"] = new_chkp
            
        # main data update WITH downsampling -----------------------------------
        if opt["downsamplex"] is not False:
            # freeze the current length of the raw data store, so that it can handle having data appended to the store while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
            idx_raw_newest = min(len(store[f"g{g}"][f"t{t}_x"]), len(store[f"g{g}"][f"t{t}_y"])) -1
            
            # determine the potential new checkpoint: finds the index of the next smaller element (to latest raw x) in the downsampled x "grid". this will be the latest downsampled point that is fully covered by raw data.
            old_chkp = chkp_traces[f"t{t}"]
            new_chkp = idx_next_smaller(store[f"g{g}"][f"t{t}_xDown"], store[f"g{g}"][f"t{t}_x"][idx_raw_newest])
            
            # only do data update and downsample if there is enough new data to cover a new xDown point
            if new_chkp > old_chkp:
                
                # find the lower end of the raw data that actually needs to be sampled. (just needs to fully cover the x downsampled interval from old_chkp to new_chkp, anything else is redundant)
                idx_raw_oldest = idx_next_smaller(store[f"g{g}"][f"t{t}_x"], store[f"g{g}"][f"t{t}_xDown"][old_chkp+1])
                
                # -------------------------------------------- main trace update
                yDown = np.interp(
                    store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1],
                    store[f"g{g}"][f"t{t}_x"][idx_raw_oldest:idx_raw_newest+1],
                    store[f"g{g}"][f"t{t}_y"][idx_raw_oldest:idx_raw_newest+1]
                )
                n2t_nr = n2t[f"g{g}"][f"t{t}_main"]
                PTCH["data"][n2t_nr]["x"].extend(list(store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1]))
                PTCH["data"][n2t_nr]["y"].extend(list(yDown))
                
                # ----------------------------------------------- endpoint trace 
                if trc[keyT]["P"] is True:
                    n2t_nr = n2t[f"g{g}"][f"t{t}_point"]
                    PTCH["data"][n2t_nr]["x"] = [store[f"g{g}"][f"t{t}_xDown"][new_chkp]]*2
                    PTCH["data"][n2t_nr]["y"] = [yDown[-1]]*2
                
                # -------------------------------------------------- error trace 
                if trc[keyT]["E"] is True:
                    yLoDown = np.interp(
                        store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1],
                        store[f"g{g}"][f"t{t}_x"][idx_raw_oldest:idx_raw_newest+1],
                        store[f"g{g}"][f"t{t}_yLo"][idx_raw_oldest:idx_raw_newest+1]
                    )
                    n2t_nr = n2t[f"g{g}"][f"t{t}_lo"]
                    PTCH["data"][n2t_nr]["x"].extend(list(store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1]))
                    PTCH["data"][n2t_nr]["y"].extend(list(yLoDown))
                    
                    yHiDown = np.interp(
                        store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1],
                        store[f"g{g}"][f"t{t}_x"][idx_raw_oldest:idx_raw_newest+1],
                        store[f"g{g}"][f"t{t}_yHi"][idx_raw_oldest:idx_raw_newest+1]
                    )
                    n2t_nr = n2t[f"g{g}"][f"t{t}_hi"]
                    PTCH["data"][n2t_nr]["x"].extend(list(store[f"g{g}"][f"t{t}_xDown"][old_chkp+1:new_chkp+1]))
                    PTCH["data"][n2t_nr]["y"].extend(list(yHiDown))
                
                chkp_traces[f"t{t}"] = new_chkp
            
        # min/max dependent line updated -------------------------------------------------------------------------------
        
        # already check if min / max has changed and reset flag to avoid missing updates. 
        hasNewMin = False
        hasNewMax = False
        if store[f"g{g}"][f"t{t}_yMinNew"] is True:
            hasNewMin       = True
            anyMinMaxChange = True
            store[f"g{g}"][f"t{t}_yMinNew"] = False
            
        if store[f"g{g}"][f"t{t}_yMaxNew"] is True:
            hasNewMax       = True
            anyMinMaxChange = True
            store[f"g{g}"][f"t{t}_yMaxNew"] = False
            
        # ------------------------------------------------- update showmin trace
        if (opt["showmin"] == keyT) and (hasNewMin is True):                 
            n2t_nr = n2t[f"g{g}"][f"t{t}_minline"]
            newMin = store[f"g{g}"][f"t{t}_yMin"]
            
            PTCH["data"][n2t_nr]["y"] = [newMin]*2
            
            # TODO: here the annotation data index is just hardcoded, maybe use mapping dict too. Not a hhuuuuge problem, since there seems to be only one annotation anyways so far
            PTCH["layout"]["annotations"][0]["text"] = f"<b> minimum:<br> {newMin:07.4f}</b>"
            PTCH["layout"]["annotations"][0]["y"] = newMin
            PTCH["layout"]["annotations"][0]["visible"] = True
        
        # ------------------------------------------------- update showmax trace
        if (opt["showmax"] == keyT) and (hasNewMax is True):    
            n2t_nr = n2t[f"g{g}"][f"t{t}_maxline"]
            newMax = store[f"g{g}"][f"t{t}_yMax"]
            
            PTCH["data"][n2t_nr]["y"] = [newMax]*2
    
            PTCH["layout"]["annotations"][0]["text"] = f"<b> maximum:<br> {newMax:07.4f}</b>"
            PTCH["layout"]["annotations"][0]["y"] = newMax
            PTCH["layout"]["annotations"][0]["visible"] = True
    
    # min/max dependent autorange updates ------------------------------------------------------------------------------
    
    # normal Figure ------------------------------------------------------------
    if (anyMinMaxChange is True) and (opt["subplots"] is False):
        # gather all mins / maxes and take the min / max over all of them (with a ceil / floor of 0)
        MIN = min([store[f"g{g}"][f"t{int(key[-1])}_yMin"] for key in trc.keys()] + [0])
        MAX = max([store[f"g{g}"][f"t{int(key[-1])}_yMax"] for key in trc.keys()] + [0])

        # ----------------------------------------------------- update autorange
        yRng = determine_single_range(MIN, MAX, factor=0.1)
        PTCH["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = yRng[0]
        PTCH["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = yRng[1]
    
    # subplot Figure -----------------------------------------------------------        
    if (anyMinMaxChange is True) and (opt["subplots"] is True):
        # gather all mins / maxes but separate for primary and secondary plot
        MIN1 = min(
            [store[f"g{g}"][f"t{int(keyT[-1])}_yMin"] if trc[keyT]["T"] == "primary" else 0 for keyT in trc] + [0]
        )
        MAX1 = max(
            [store[f"g{g}"][f"t{int(keyT[-1])}_yMax"] if trc[keyT]["T"] == "primary" else 0 for keyT in trc] + [0]
        )
        MIN2 = min(
            [store[f"g{g}"][f"t{int(keyT[-1])}_yMin"] if trc[keyT]["T"] == "secondary" else 0 for keyT in trc] + [0]
        )
        MAX2 = max(
            [store[f"g{g}"][f"t{int(keyT[-1])}_yMax"] if trc[keyT]["T"] == "secondary" else 0 for keyT in trc] + [0]
        )

        # ----------------------------------------------------- update autorange
        yRng1        = determine_single_range(MIN1, MAX1, factor=0.1)
        yRng2        = determine_single_range(MIN2, MAX2, factor=0.1)
        yRng1, yRng2 = determine_mixed_range(yRng1, yRng2)
        PTCH["layout"]["yaxis"]["autorangeoptions"]["minallowed"]  = yRng1[0]
        PTCH["layout"]["yaxis"]["autorangeoptions"]["maxallowed"]  = yRng1[1]
        PTCH["layout"]["yaxis2"]["autorangeoptions"]["minallowed"] = yRng2[0]
        PTCH["layout"]["yaxis2"]["autorangeoptions"]["maxallowed"] = yRng2[1]
        
    
    return PTCH, chkp_traces

def callback_update_proc_speed(store: dict):
    proc_speed = store["proc"]["speed"]
    
    if len(proc_speed) == 0:
        return [f"---'---.-- samples/sec"]
    
    avg_speed = sum(proc_speed) / len(proc_speed)
    return [f"{avg_speed:,.2f} samples/sec".replace(",", "'")]

