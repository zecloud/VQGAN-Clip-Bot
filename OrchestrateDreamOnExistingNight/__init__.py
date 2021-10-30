# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json
from typing import Dict
import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    orchRequest:Dict[str,str]  =context.get_input()
    
    containerGroupName="vqganclip-demo"
    status = yield context.call_activity("VerifyDreamStatus",containerGroupName)
    job_status=status[0]
    container_status = status[1]
    if(str(job_status).lower()=="succeeded" and str(container_status).lower() =="running"):
        exec_result = yield context.call_activity("GenerateImageOnExistingNight",orchRequest)
    

main = df.Orchestrator.create(orchestrator_function)