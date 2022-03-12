# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import os
from .. import experiment
from typing import Dict
import azure.functions as func
import json

def main(imagine:  Dict[str,str],exportImage:func.Out[bytes],exportVid:func.Out[bytes],notifyFrontSignalR: func.Out[str]) -> str:

    prefixpath="/outputs/"
    exppath=experiment.to_experiment_name(imagine["phrase"])
    it =int(imagine["iterations"])
    if(it<100):
        steps = "0"+str(it-1)
    else:
        steps= str(it-1)
    finalpath=prefixpath+exppath +"/steps/"+steps+".png"
    videopath=prefixpath+exppath+"/video.mp4"
    progresspath=prefixpath+exppath+"/progress.png"
    finished=os.path.exists(finalpath)
    if(finished):
        with open(finalpath,'rb') as f:   
            exportImage.set(f.read())
        with open(videopath,'rb') as f:   
            exportVid.set(f.read())  
    else:
        if(os.path.exists(progresspath)):
            with open(progresspath,'rb') as f:   
                exportImage.set(f.read())
    return finished
