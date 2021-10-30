# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
from typing import Dict
import logging
import os.path
import azure.functions as func
import json 
from .. import experiment


def main(imagine:  Dict[str,str],msgout:func.Out[func.QueueMessage]) -> str:
    id,ext = os.path.splitext(imagine["initImage"])
    dream=experiment.to_experiment_name(imagine["phrase"])

    dreamcomplete={'id':id,'dream':dream,'origincontainer':imagine["origincontainer"]}
    msgout.set(json.dumps(dreamcomplete))
    return f"Dream Complete!"
