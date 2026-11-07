import os
import sys
from   pathlib import Path

from mldashboard.containers.datastore import Store
from mldashboard.containers.datastore import GraphStore
from mldashboard.containers.datastore import TraceData


if __name__ == "__main__":
    os.system("cls" if os.name=="nt" else "clear")
    
    # store = DataStore(
    #     graph1=GraphStore(
    #         traces=[
    #             TraceStore(),
    #             TraceStore()
    #         ]
    #     ),
    #     graph2=GraphStore(
    #         traces=[
                
    #         ]
    #     ),
    #     graph3=GraphStore(
    #         traces=[
                
    #         ]
    #     )
    # )

    