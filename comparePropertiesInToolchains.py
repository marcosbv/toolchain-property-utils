import os
import sys
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_continuous_delivery import CdToolchainV2, CdTektonPipelineV2

resource_group_id=os.getenv('RG', '3259d0bd537a4637906824892ef935ac')

service_url_base=os.getenv('SERVICE_URL_BASE', 'https://api.br-sao.devops.cloud.ibm.com')
toolchain_name_first=sys.argv[1]
toolchain_name_second=sys.argv[2]
pipeline_name_first=sys.argv[3]

tokenAuth = BearerTokenAuthenticator(os.getenv('IBMCLOUD_TOKEN'))
toolchain_service = CdToolchainV2(tokenAuth)
tool_service = CdTektonPipelineV2(tokenAuth)

toolchain_service.set_service_url(f"{service_url_base}/toolchain/v2")
tool_service.set_service_url(f"{service_url_base}/pipeline/v2")

toolchains=toolchain_service.list_toolchains(resource_group_id=resource_group_id, limit=200)

properties_from_first_pipeline={}
properties_from_second_pipeline={}

for toolchain in toolchains.result['toolchains']:
    if toolchain['name'] == toolchain_name_first:
        toolchain_tools = toolchain_service.list_tools(toolchain_id=toolchain['id'], limit=100)
        for toolchain_tool in toolchain_tools.result['tools'] :
            if toolchain_tool['tool_type_id'] == 'pipeline':
               if toolchain_tool['parameters']['label'] == pipeline_name_first:
                   tool=tool_service.get_tekton_pipeline(id=toolchain_tool['id'])
                   for property in tool.result['properties'] :
                       properties_from_first_pipeline[property['name']] = property['value']

for toolchain in toolchains.result['toolchains']:
    if toolchain['name'] == toolchain_name_second:
        toolchain_tools = toolchain_service.list_tools(toolchain_id=toolchain['id'], limit=100)
        for toolchain_tool in toolchain_tools.result['tools'] :
            if toolchain_tool['tool_type_id'] == 'pipeline':
               if toolchain_tool['parameters']['label'] == pipeline_name_first:
                   tool=tool_service.get_tekton_pipeline(id=toolchain_tool['id'])
                   for property in tool.result['properties'] :
                       properties_from_second_pipeline[property['name']] = property['value']

#print(properties_from_first_pipeline) 
#print(properties_from_second_pipeline)

for property in properties_from_first_pipeline.keys():
    if property in properties_from_second_pipeline:
        if properties_from_first_pipeline[property] != properties_from_second_pipeline[property] :
            print(f"""Property {property} values are different: 
                p1={properties_from_first_pipeline[property]} 
                p2={properties_from_second_pipeline[property]}""")
    else:
        print(f">>>Property {property} not found in the second pipeline>>>\n")

for property in properties_from_second_pipeline.keys():
    if property not in properties_from_second_pipeline:
        print(f"<<<Property {property} not found in the first pipeline<<<\n")

