import os
import sys
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_continuous_delivery import CdToolchainV2, CdTektonPipelineV2

resource_group_id=os.getenv('RG', '3259d0bd537a4637906824892ef935ac')

service_url_base=os.getenv('SERVICE_URL_BASE', 'https://api.br-sao.devops.cloud.ibm.com')
toolchain_name_first=sys.argv[1]
toolchain_name_second=sys.argv[2]
pipeline_name_first=sys.argv[3]

propertiesToSync=sys.argv[4].split(",")

tokenAuth = BearerTokenAuthenticator(os.getenv('IBMCLOUD_TOKEN'))
toolchain_service = CdToolchainV2(tokenAuth)
tool_service = CdTektonPipelineV2(tokenAuth)

toolchain_service.set_service_url(f"{service_url_base}/toolchain/v2")
tool_service.set_service_url(f"{service_url_base}/pipeline/v2")

toolchains=toolchain_service.list_toolchains(resource_group_id=resource_group_id, limit=200)

properties_from_first_pipeline={}
properties_from_second_pipeline={}

pipeline_id_second=None

for toolchain in toolchains.result['toolchains']:
    if toolchain['name'] == toolchain_name_first:
        toolchain_tools = toolchain_service.list_tools(toolchain_id=toolchain['id'], limit=100)
        for toolchain_tool in toolchain_tools.result['tools'] :
            if toolchain_tool['tool_type_id'] == 'pipeline':
               if toolchain_tool['parameters']['label'] == pipeline_name_first:
                   tool=tool_service.get_tekton_pipeline(id=toolchain_tool['id'])
                   for property in tool.result['properties'] :
                       properties_from_first_pipeline[property['name']] = property

for toolchain in toolchains.result['toolchains']:
    if toolchain['name'] == toolchain_name_second:
        toolchain_tools = toolchain_service.list_tools(toolchain_id=toolchain['id'], limit=100)
        for toolchain_tool in toolchain_tools.result['tools'] :
            if toolchain_tool['tool_type_id'] == 'pipeline':
               if toolchain_tool['parameters']['label'] == pipeline_name_first:
                   pipeline_id_second=toolchain_tool['id']
                   tool=tool_service.get_tekton_pipeline(id=pipeline_id_second)
                   for property in tool.result['properties'] :
                       properties_from_second_pipeline[property['name']] = property

#print(properties_from_first_pipeline) 
#print(properties_from_second_pipeline)

for propertyToSync in propertiesToSync:
    if propertyToSync not in properties_from_first_pipeline:
        print("Property not found in the source pipeline... Skipping...")
        continue
    if propertyToSync not in properties_from_second_pipeline:
        print(f"""Property {propertyToSync} not found in the target pipeline... Creating new variable there:
              type={properties_from_first_pipeline[propertyToSync]['type']}
              value={properties_from_first_pipeline[propertyToSync]['value']}""")
        p=properties_from_first_pipeline[propertyToSync]
        tool_service.create_tekton_pipeline_properties(pipeline_id=pipeline_id_second, 
                                                       name=properties_from_first_pipeline[propertyToSync]['name'],
                                                       type=properties_from_first_pipeline[propertyToSync]['type'],
                                                       value=properties_from_first_pipeline[propertyToSync]['value'])
    else:
        if properties_from_first_pipeline[propertyToSync]['type'] == "secure" :
            print(f">>>Skipping secure variable {propertyToSync}. Please change it manually...")
            continue
        print(f"""Replacing property {propertyToSync} 
              oldValue={properties_from_second_pipeline[propertyToSync]['value']}
              newValue={properties_from_first_pipeline[propertyToSync]['value']}""")
        tool_service.replace_tekton_pipeline_property(pipeline_id=pipeline_id_second, 
                                                      name=properties_from_second_pipeline[propertyToSync]['name'],
                                                      property_name=properties_from_second_pipeline[propertyToSync]['name'],
                                                      type=properties_from_second_pipeline[propertyToSync]['type'],
                                                      value=properties_from_first_pipeline[propertyToSync]['value'])
