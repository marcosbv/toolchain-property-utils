# Utility to compare toolchain pipeline variables and sync variables

This utility allows teams to look for differences into variable values and synchronize toolchain values when pipeline migration is required.

## Requirements

* Python 3.9 or newer
* IBM Cloud CLI installed

It could be run from IBM Cloud Shell for convenience. 

## Installation

From this folder, run: 

```
./pythonSetup.sh
```

This installs the dependencies.

## Environment Setup

First, your IBM Cloud CLI must be logged in. If using IBM Cloud CLI, this is done as soon as the session is initiated.
You can login by using the following command:

````
ibmcloud login --sso
````
Then, run the environment setup passing the Resource Group linked to the your toolchains.

````
source envSetup.sh {Toolchain_RG_Name}
````

That script initializes IBMCLOUD_TOKEN containing a Bearer token and RG containing the Resource Group ID based on name. Bearer tokens are short-lived tokens (usually 15 minutes), so after it is expired, envSetup.sh must be re-run. If it can't retrieve a token, then you must re-login by using ibmcloud CLI and then re-run emvSetup.sh.

## Compare Properties in Toolchains

Usage:

```
python3 comparePropertiesInToolchains.py {Toolchain_1_Name} {Toolchain_2_Name} {Pipeline_Name}
```

This command checks all properties in a given pipeline name in 2 different toolchains, reporting non-existent properties in one of the sides or different values found in the same property. The outputs could be like below:

Different properties:
```
Property app-deployment-timeout values are different: 
                p1=300 <---- value in toolchain 1
                p2=100 <---- value in toolchain 2
```

Non-existent properties:
````
### Property existent in Toolchain_1, not existent in Toolchain_2
>>>Property xyz not found in the second pipeline>>>

### Property existent in Toolchain_2, but missing in Toolchain_1
<<<Property xyz not found in the first pipeline<<<
````


Example:
````
python3 comparePropertiesInToolchains.py npr-br-sao-cotoms-cci npr-br-sao--cotoms-v8-cci ci-pipeline
````

## Synchronize Properties in Toolchain (TODO)