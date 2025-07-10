######
## Setup Resource Group ID and IBM Cloud Token
##
## Dependencies: IBM Cloud CLI
## Usage: ./envSetup.sh <RG_NAME> 
######

export IBMCLOUD_TOKEN=$(ibmcloud iam oauth-tokens|grep Bearer|cut -d ' ' -f5)
export RG=$(ibmcloud resource groups | grep $1 | cut -c 33-64)

echo "Environment Variables ready. You can use the following Python commands to analyze your pipelines:"
echo "python3 comparePropertiesInToolchain.py {Toolchain_1} {Toolchain_2} {Pipeline_Name}"
echo "python3 syncPropertiesInToolchain.py {Toolchain_1} {Toolchain_2} {Pipeline_Name} {Comma_Delimited_List_Properties_To_Sync}"
echo ""
echo "Bearer tokens are shorted-lived (usually 15 minutes). In case you receive 401 errors, please reauthenticate IBM Cloud CLI and re-run envSetup.sh."