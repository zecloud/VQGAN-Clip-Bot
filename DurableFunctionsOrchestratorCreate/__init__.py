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
    
    containerGroupName =yield context.call_activity('Generate_images', orchRequest)

    expiry_time = context.current_utc_datetime + timedelta(minutes=120)
    while context.current_utc_datetime < expiry_time:
        job_status = yield context.call_activity("VerifyDreamStatus",containerGroupName)
        logging.info(str(job_status))
        if str(job_status).lower()  == "succeeded":
            logging.info("Job Complete " + str(job_status))
            yield context.call_activity('CopyFinishedDream', orchRequest)
            finallog=yield context.call_activity("Clean",containerGroupName)
            logging.info(finallog)
            break
        elif str(job_status).lower() == "failed":
            logging.info("Job Failed " + str(job_status))
            raise Exception("Job failed.")
            #break
        else:
            next_check = context.current_utc_datetime + timedelta(minutes=1)
            context.set_custom_status("pendingContainer")
            yield context.create_timer(next_check)
            logging.info("Job " + str(job_status))
    
    return job_status 

   

main = df.Orchestrator.create(orchestrator_function)