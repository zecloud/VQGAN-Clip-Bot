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
    trycount=0
    expiry_time = context.current_utc_datetime + timedelta(minutes=120)
    while context.current_utc_datetime < expiry_time:
        status = yield context.call_activity("VerifyDreamStatus",containerGroupName)
        job_status=status[0]
        logging.info(str(job_status))
        if str(job_status).lower()  == "succeeded":
            context.set_custom_status("ContainerStarted")
            container_status = status[1]
            if(str(container_status).lower()=="succeeded"):
                context.set_custom_status("succeeded")
                yield context.call_activity('CopyFinishedDream', orchRequest)
                finallog=yield context.call_activity("Clean",containerGroupName)
                logging.info(finallog)
                break
            elif(str(container_status).lower()=="failed"):
                logging.info("Container "+str(container_status))
                #finallog=yield context.call_activity("Clean",containerGroupName)
                #logging.info(finallog)
                if(trycount==1):
                   raise Exception("Job failed.")
                else:
                   containerGroupName =yield context.call_activity('Generate_images', orchRequest)
                   trycount=trycount+1
            elif(str(container_status).lower()=="stopped"):
                logging.info("Job "+str(job_status))
                logging.info("Exiting")
                break
            logging.info("Container "+str(container_status))
            
        elif str(job_status).lower() == "failed":
            logging.info("Job Failed " + str(job_status))
            raise Exception("Provisioning failed.")
        next_check = context.current_utc_datetime + timedelta(minutes=1)
        context.set_custom_status("pendingContainer")
        yield context.create_timer(next_check)
       
    return job_status 

   

main = df.Orchestrator.create(orchestrator_function)