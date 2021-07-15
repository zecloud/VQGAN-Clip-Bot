import logging
import json
import azure.functions as func
import azure.durable_functions as df
import os.path

async def  main(msg: func.QueueMessage,client:str,inputImage:bytes) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    client = df.DurableOrchestrationClient(client)
    payload = json.loads(msg.get_body().decode('utf-8'))
    path="/outputs/"+payload["initImage"]
    with open(path,'wb+') as f:
        f.write(inputImage)
    instance_id = await client.start_new("DurableFunctionsOrchestratorCreate", None, client_input=payload)
    




    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    
