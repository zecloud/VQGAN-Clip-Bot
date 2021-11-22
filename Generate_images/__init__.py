# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from .. import LaunchContainer
import azure.functions as func
import json
from typing import Dict

def main(imagine:  Dict[str,str],notifyFrontSignalR: func.Out[str]) -> str:
    
    containerGroupName =LaunchContainer.launchVqganClipWithPhrase(phrase=imagine["phrase"],
    initImage=imagine.get("initImage",None),
    model=imagine.get("model",None),
    iterations=imagine.get("iterations",None),
    size=imagine.get("size",None))
    if(imagine.get("dream_id",False)):
        notifyFrontSignalR.set(json.dumps({
            'target': 'newContainerStatus',
            'arguments': [{'id':imagine["dream_id"],'status':'Container Group started'}]
        }))
    return containerGroupName
