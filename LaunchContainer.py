import random
import string
import time
import sys
from os import getenv,environ, initgroups
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
#from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup,
                                                 Container,
                                                 ContainerGroupNetworkProtocol,
                                                 ContainerGroupRestartPolicy,
                                                 ContainerPort,
                                                 EnvironmentVariable,
                                                 Port,
                                                 VolumeMount,
                                                 Volume,
                                                 AzureFileVolume,
                                                 ResourceRequests,
                                                 GpuResource,
                                                 ImageRegistryCredential,
                                                 ResourceRequirements,
                                                 OperatingSystemTypes)
from six import string_types


def run_task_based_container(aci_client, resource_group, container_group_name,
                             container_image_name, start_command_line=None):
    """Creates a container group with a single task-based container who's
       restart policy is 'Never'. If specified, the container runs a custom
       command line at startup.
    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                    -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                    -- The resource group in which to create the container group.
        container_group_name {str}
                    -- The name of the container group to create.
        container_image_name {str}
                    -- The container image name and tag, for example:
                       microsoft\aci-helloworld:latest
        start_command_line {str}
                    -- The command line that should be executed when the
                       container starts. This value can be None.
    """
    # If a start command wasn't specified, use a default
    if start_command_line is None:
        start_command_line = ["/bin/bash", "-c", "mkdir test; touch test/myfile; tail -f /dev/null"] #["python", "generate_images.py", "-m","wikiart","-i","Make neural networks dreams come true","--init_image","/tf/outputs/IMG_20210711_161242-sm.jpg","--save_video","--overwrite","--size","512","512","--iterations","500"]#"python wordcount.py http://shakespeare.mit.edu/romeo_juliet/full.html"

    # Configure some environment variables in the container which the
    # wordcount.py or other script can read to modify its behavior.
    #env_var_1 = EnvironmentVariable(name='NumWords', value='5')
    #env_var_2 = EnvironmentVariable(name='MinLength', value='8')

    print("Creating container group '{0}' with start command '{1}'"
          .format(container_group_name, start_command_line))

    gpu_res= GpuResource(count=1,sku=environ["SKUGPU"])
    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb=16, cpu=1.0,gpu=gpu_res)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)
    container_volume_mounts=[
        VolumeMount(name="modelsvolume",mount_path="/tf/models"),
        VolumeMount(name="outputsvolume",mount_path="/tf/outputs")
    ]
    container = Container(name=container_group_name,
                          image=container_image_name,
                          resources=container_resource_requirements,
                          command=start_command_line,#.split(),
                          volume_mounts=container_volume_mounts)
                          #environment_variables=[env_var_1, env_var_2])

    share_volumes=[
        Volume(name="modelsvolume",azure_file=AzureFileVolume(share_name="vqmodels",storage_account_name="gangoghhd",storage_account_key=environ["STORAGEKEY"])),
        Volume(name="outputsvolume",azure_file=AzureFileVolume(share_name="vqoutputs",storage_account_name="gangoghhd",storage_account_key=environ["STORAGEKEY"]))
    ]
    image_registry=[ImageRegistryCredential(server="zecloud.azurecr.io",username="zecloud",password=environ["REGISTRYPASSWORD"])]
    # Configure the container group
    group = ContainerGroup(location=resource_group.location,
                           containers=[container],
                           volumes=share_volumes,
                           image_registry_credentials=image_registry,
                           os_type=OperatingSystemTypes.linux,
                           restart_policy=ContainerGroupRestartPolicy.never)

    # Create the container group
    result = aci_client.container_groups.begin_create_or_update(resource_group.name,
                                                          container_group_name,
                                                          group)

    # Wait for the container create operation to complete. The operation is
    # "done" when the container group provisioning state is one of:
    # Succeeded, Canceled, Failed
    #result.wait()
    # while result.done() is False:
    #     sys.stdout.write('.')
    #     time.sleep(1)

    


def launchVqganClipWithPhrase(phrase,initImage=None,model=None,iterations=None,size=None):
    run_command=["python", "generate_images.py", "-i",phrase,"--save_video","--overwrite"]
    if(initImage):
         run_command.extend(["--init_image","/tf/outputs/"+initImage])
    if(model):
        run_command.extend(["-m",model])
    if(iterations):
        run_command.extend(["--iterations",iterations])
    if(size):
        size.insert(0,"--size")
        run_command.extend(size)

    container_image_app = environ["containerimage"]
    resource_group_name = environ["resgroup"]
    container_group_name = 'vqgan-' + ''.join(random.choice(string.digits)
                                                for _ in range(6))
    credential = DefaultAzureCredential()
    resclient=ResourceManagementClient(credential=credential,subscription_id=environ["AZURE_SUBSCRIPTION_ID"])
    aciclient=ContainerInstanceManagementClient(credential=credential,subscription_id=environ["AZURE_SUBSCRIPTION_ID"])
    resource_group = resclient.resource_groups.get(resource_group_name)
    run_task_based_container(aciclient, resource_group,
                            container_group_name,
                            container_image_app,
                            run_command)
    return container_group_name

def getProvisioningState(container_group_name=None):
    credential = DefaultAzureCredential()
    resource_group_name = environ["resgroup"]
    aciclient=ContainerInstanceManagementClient(credential=credential,subscription_id=environ["AZURE_SUBSCRIPTION_ID"])
    # Get the provisioning state of the container group.
    container_group = aciclient.container_groups.get(resource_group_name,
                                                      container_group_name)
    return container_group.provisioning_state

def getContainerState(container_group_name=None):
    credential = DefaultAzureCredential()
    resource_group_name = environ["resgroup"]
    aciclient=ContainerInstanceManagementClient(credential=credential,subscription_id=environ["AZURE_SUBSCRIPTION_ID"])
    container_group = aciclient.container_groups.get(resource_group_name,
                                                      container_group_name)
    return container_group.instance_view.state


def removeContainerGroupFinished(container_group_name):
    credential = DefaultAzureCredential()
    resource_group_name = environ["resgroup"]
    aciclient=ContainerInstanceManagementClient(credential=credential,subscription_id=environ["AZURE_SUBSCRIPTION_ID"])
    # Get the logs for the container
    logs = aciclient.containers.list_logs(resource_group_name,
                                          container_group_name,
                                          container_group_name)
    finallog= logs.content
    # print("Logs for container '{0}':".format(container_group_name))
    # print("{0}".format(logs.content))
    aciclient.container_groups.begin_delete(resource_group_name,container_group_name)
    return finallog

    
    # if str(container_group.provisioning_state).lower() == 'succeeded':
    #     return("\nCreation of container group '{}' succeeded."
    #           .format(container_group_name))
    # else:
    #     return("\nCreation of container group '{}' failed. Provisioning state"
    #           "is: {}".format(container_group_name,
    #                           container_group.provisioning_state))

    # Get the logs for the container
    # logs = aci_client.container.list_logs(resource_group.name,
    #                                       container_group_name,
    #                                       container.name)

    # print("Logs for container '{0}':".format(container_group_name))
    # print("{0}".format(logs.content))
