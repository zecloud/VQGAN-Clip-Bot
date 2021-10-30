# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

from datetime import timedelta
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
    expiry_time = context.current_utc_datetime + timedelta(minutes=20)
    while context.current_utc_datetime < expiry_time:
        finished=yield context.call_activity("ExportImages",orchRequest)
        if(finished):
            yield context.call_activity("CleanImages",orchRequest)
            #clean
            break
        next_check = context.current_utc_datetime + timedelta(minutes=1)
        context.set_custom_status("DreamInProgress")
        yield context.create_timer(next_check)
    

main = df.Orchestrator.create(orchestrator_function)