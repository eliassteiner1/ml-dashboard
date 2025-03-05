
""" the following is the prototype for updating all the necessary graph properties with just a patch! this is already muuuuuuch more efficient than full redraws, but still, it starts becoming a low of load for the visual rendering when having much more than 10k points"""

@app.callback(
    Output("graph-cardA", "figure"),
    Output("graph-cardB", "figure"),
    Output("graph-cardC", "figure"),
    Output("checkpoint", "data"),
    Input("ud-interval", "n_intervals"),
    State("checkpoint", "data"),
    prevent_initial_call=True
)
@perf_timer
def update_graph_patched(n, old_chkp):
    
    if len(store["x"]) <= 0:
        return no_update
    
    # grab the current length of the store to handle data being appended to store in the meantime!
    idxx = len(store["x"]) - 1
    
    # downsample data
    lastidx = np.searchsorted(store["x_down"], store["x"][idxx])-1 # find last coarse grid point with full data avail!
    x_down  = store["x_down"]
    y_down  = np.interp(x_down[0:lastidx+1], store["x"][0:idxx+1], store["y"][0:idxx+1])
    
    x_down = store["x"][0:idxx+1]
    y_down = store["y"][0:idxx+1]
    
    
    # grab index of newest available datapoint
    new_chkp = len(y_down)
    
    ptch = Patch()
    # maybe add some if block, that REPLACES data when old chkp is 0, to remove any initial Nones
    if new_chkp > old_chkp: # only update if new data is available
        # Append new data to the first trace (index 0)
        ptch["data"][0]["x"].extend(list(x_down[old_chkp:new_chkp]))
        ptch["data"][0]["y"].extend(list(y_down[old_chkp:new_chkp]))
        
        # change the trace data for the endpoint trace (idx 1)
        ptch["data"][1]["x"] = [x_down[new_chkp-1]]
        ptch["data"][1]["y"] = [y_down[new_chkp-1]]
        
        # change the trace data for the bestline trace (idx 2)
        new_min = min(y_down[:new_chkp])
        ptch["data"][2]["y"] = [new_min]*2
        
        # modify the annotation for the bestvalue (apparently they also have indices like traces)
        ptch["layout"]["annotations"][0]["text"] = f"<b> lowest:<br> {new_min:07.4f}</b>"
        ptch["layout"]["annotations"][0]["y"] = new_min
    
        # patch the range (yaxis and yaxis2 for subplots)
        new_min = min(list(y_down[:new_chkp]))
        new_max = max(list(y_down[:new_chkp]))
        ptch["layout"]["yaxis"]["autorangeoptions"]["minallowed"] = new_min - 1.0
        ptch["layout"]["yaxis"]["autorangeoptions"]["maxallowed"] = new_max + 1.0

    return ptch, ptch, ptch, new_chkp


""" the following is a prototype for an update callback for one fig and ONE trace that supports either downsampling or writing out the full raw data 

probably necessary to adapt to multiple traces: but for ONE fig: crete the empty patch, then have the downsampling fork. in each case (respectively) loop through all the traces, adding to the patch whenever an update is neccessary. """

@app.callback(
    Output("graph-cardA", "figure"),
    Output("checkpoint", "data"),
    Input("ud-interval", "n_intervals"),
    State("checkpoint", "data"),
    prevent_initial_call=True
)
def update_graph_patched(n, old_chkp):
    DO_DOWNSAMPLE = True
    ptch = Patch()
    
    if len(store["x"]) == 0: # exit when no data is available (avoids errors in subsequent code)
        return ptch, no_update 
    
    if DO_DOWNSAMPLE is False:
        # freeze the current length of the store, to handle data being appended while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
        idx_raw_newest = len(store["x"]) - 1 
        new_chkp       = idx_raw_newest
        
        # exit with no update if absolutely now new data samples are available
        if new_chkp <= old_chkp:
            return ptch, no_update
        
        # create the patch entry for appending data (tr idx 0)
        ptch["data"][0]["x"].extend(list( store["x"][old_chkp+1:new_chkp+1] ))
        ptch["data"][0]["y"].extend(list( store["y"][old_chkp+1:new_chkp+1] ))
        
    if DO_DOWNSAMPLE is True:
        # freeze the current length of the store, to handle data being appended while this callback runs. It can actually happen, that data is appended in between accessing storex and storey, so that they have unequal length! (can use either x or y length)
        idx_raw_newest = len(store["x"]) - 1 
        
        # determine the potential new checkpoint: finds the index of the next smaller element (to latest raw x) in the downsampled x "grid". this will be the latest downsampled point that is fully covered by raw data
        new_chkp = get_idx_next_smaller(store["x_down"], store["x"][idx_raw_newest])
        
        # exit with no update, if the new raw data doesn't cover a full downsampled x interval
        if new_chkp <= old_chkp:
            return ptch, no_update
        
        # find the lower end of the raw data that actually needs to be sampled. (just needs to fully cover the x downsampled interval from old_chkp to new_chkp, anything else is redundant)
        idx_raw_oldest = get_idx_next_smaller(store["x"], store["x_down"][old_chkp+1])
        
        # actually downsample the data
        y_down = np.interp(
            store["x_down"][old_chkp+1:new_chkp+1],
            store["x"][idx_raw_oldest:idx_raw_newest+1],
            store["y"][idx_raw_oldest:idx_raw_newest+1]
            )
        
        # create the patch entry for appending data (tr idx 0)
        ptch["data"][0]["x"].extend(list( store["x_down"][old_chkp+1:new_chkp+1] ))
        ptch["data"][0]["y"].extend(list( y_down ))

        # change the trace data for the endpoint trace (tr idx 1)
        ptch["data"][1]["x"] = [store["x_down"][new_chkp]]
        ptch["data"][1]["y"] = [y_down[-1]]
        
    return ptch, new_chkp