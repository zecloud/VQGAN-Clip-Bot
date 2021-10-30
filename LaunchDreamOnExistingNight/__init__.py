import logging
import azure.functions as func
import azure.durable_functions as df
import requests

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    instance_id = req.route_params['instanceId']
    function_name = req.route_params['functionName']
    existing_instance = await client.get_status(instance_id)

    if existing_instance.runtime_status in [df.OrchestrationRuntimeStatus.Completed, df.OrchestrationRuntimeStatus.Failed, df.OrchestrationRuntimeStatus.Terminated, None]:
        payload =req.get_json()
        path=payload["initImage"]#"/outputs/"+
        url_imgsrc=payload["url_imgsrc"]
        response = requests.get(url_imgsrc)
        with open(path,'wb+') as f:
            f.write(response.content)

        instance_id = await client.start_new(function_name, instance_id, payload)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)
    else:
        return {
            'status': 409,
            'body': f"An instance with ID '${existing_instance.instance_id}' already exists"
        }