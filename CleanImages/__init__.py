# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import shutil
from .. import experiment
from typing import Dict

def main(imagine:  Dict[str,str]) -> str:
    prefixpath="/outputs/"
    exppath=prefixpath+experiment.to_experiment_name(imagine["phrase"])
    if(exppath!=prefixpath):
        shutil.rmtree(exppath)
