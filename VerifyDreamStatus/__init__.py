# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from os import stat
from .. import LaunchContainer
import azure.functions as func
import json

def main(cname: tuple,notifyFrontSignalR: func.Out[str]) -> str:
    name=cname[0]
    provisioningState=LaunchContainer.getProvisioningState(name)
    containerState=LaunchContainer.getContainerState(name)
    if(len(cname)==2):
        if(provisioningState=="Pending"):
            status="Provisioning"
        elif(provisioningState=="Creating"):
            status="Pulling Container"
        elif(provisioningState=="Succeeded" and containerState=="Succeeded"):
            status="Succeeded"
        elif(provisioningState=="Succeeded" and containerState=="Running"):
            status=containerState
        else:
            status='Container group is '+provisioningState + ' & Container is ' + containerState
        notifyFrontSignalR.set(json.dumps({
            'target': 'newContainerStatus',
            'arguments': [{'id':cname[1],'status':status}]
        }))
    return (provisioningState,containerState)
