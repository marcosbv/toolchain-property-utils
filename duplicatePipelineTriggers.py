###
## Usage: python3 duplicatePipelineSteps {Toolchain_Name} {Pipeline_Name} "{Comma-Delimited_List_Steps_To_Duplicate}" {Environment_Name} {Properties_File_Template}
###

import os
import sys
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_continuous_delivery import CdToolchainV2, CdTektonPipelineV2
import json

resource_group_id=os.getenv('RG', '3259d0bd537a4637906824892ef935ac')

service_url_base=os.getenv('SERVICE_URL_BASE', 'https://api.br-sao.devops.cloud.ibm.com')
toolchain_name_first=sys.argv[1]
pipeline_name_first=sys.argv[2]
steps_to_duplicate=sys.argv[3]
environment_name=sys.argv[4]
template_file=sys.argv[5]

tokenAuth = BearerTokenAuthenticator(os.getenv('IBMCLOUD_TOKEN'))
toolchain_service = CdToolchainV2(tokenAuth)
tool_service = CdTektonPipelineV2(tokenAuth)

toolchain_service.set_service_url(f"{service_url_base}/toolchain/v2")
tool_service.set_service_url(f"{service_url_base}/pipeline/v2")

toolchains=toolchain_service.list_toolchains(resource_group_id=resource_group_id, limit=200)

properties_from_first_pipeline={}

for toolchain in toolchains.result['toolchains']:
    if toolchain['name'] == toolchain_name_first:
        toolchain_tools = toolchain_service.list_tools(toolchain_id=toolchain['id'], limit=100)
        for toolchain_tool in toolchain_tools.result['tools'] :
            if toolchain_tool['tool_type_id'] == 'pipeline':
               if toolchain_tool['parameters']['label'] == pipeline_name_first:
                   tool=tool_service.get_tekton_pipeline(id=toolchain_tool['id'])
                   for step_name in steps_to_duplicate.split(","):
                       step=tool_service.list_tekton_pipeline_triggers(pipeline_id=tool.result['id'], name=step_name)
                       if len(step.result['triggers']) > 0:
                           trigger = step.result['triggers'][0]
                           #print(trigger)
                           #print(tool.result['id'])
                           newTriggerName=f"{trigger['name']} - {environment_name.upper()}"
                           print(f"Creating new duplicated trigger from '{step_name}' trigger (pipeline_id={tool.result['id']}, trigger_id={trigger['id']}, new_trigger_name={newTriggerName})")
                           newTrigger = tool_service.duplicate_tekton_pipeline_trigger(pipeline_id=tool.result['id'],
                                                                          source_trigger_id=trigger['id'],
                                                                          name=newTriggerName)
                           print(f"New trigger created. ID={newTrigger.result['id']}")
                           ## Read properties file
                           fileP=open(template_file, 'r')
                           propertyObj=json.load(fileP)
                           for property in propertyObj:
                               print(f"Adding property: {property['name']} = {property['value']}")
                               tool_service.create_tekton_pipeline_trigger_properties(pipeline_id=tool.result['id'],
                                                                                      trigger_id=newTrigger.result['id'],
                                                                                      name=property['name'],
                                                                                      type='text',
                                                                                      value=property['value']
                                                                                      )
print("**** END OF EXECUTION ***** ")