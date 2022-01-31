# IONOS Dynamic Inventory

This is a personal attempt to create a decent Dynamic Inventory for IONOS Public Cloud
The features so far:
- With --list will show groups made by hosts in the same Virtual Data Center, grouped by the Virtual Data Center's Name
- With --list will show groups made by single host, grouped by the server's Name
- With --dc DC_UUID will show all servers RUNNINNG connected to a Public Network in a specific VDC 
- With --off will show a list of all the servers in SHUTDOWN state connected to a public network (NOT FOR INVENTORY PURPOSES)
- With --off --dc DC_UUID will shows all the servers in SHUTDOWN state connected to a public network for a specific VDC

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Test your setup](#test-your-setup)

## Description

IONOSinventory.py is an Ansible dynamic inventory, able to generate JSON output from requests sent to the using n external inventory system that can generate a proper JSON output from the Ionos API infrastructure.

## Installation

No special install procedure is required. 
The script can be used stand-alone or with Ansible
The IONOSinventory.py has been tested with Python 3.8

## Configuration

To use the scrip is recommended to export your IONOS credential for a user with admin access as environment variables:
```
export IONOS_USERNAME="your@username.com" && export IONOS_PASSWORD="your password"
```
or
Is possible to specify username and password inside the file itself (recommended ONLY for dev purposes)
```
#################################################
## You can configure username and password here##
#################################################
#username=""
#password=""
#################################################
```
or
If none of the two options above have been set-up, the script will request user input username and password.

It is also possible to change the API end-point URL; there is no need right now as the script has been design for the latest version of the API end-point (v6.0), and this functionality is reserved for future use.
```
apiEp="https://api.ionos.com/cloudapi/v6"
```

## Usage

IONOSinventory.py exposes by default the `--list` functionality required by the Ansible inventory system.

In this mode, the IONOSinventory.py will expose all the servers with state RUNNING with one connection to Public Network, grouped by Virtual Data Center and by Name.

The script will also allow you to work on all the hosts of a single VDC using the option `--dc VDC_UUID`

## Test your setup
Is it possible to run the script stand-alone against the IONOS API to verify if the username and password used
are working as expected in terms of accessing resources

```
$ export IONOS_USERNAME="your@username.com" && export IONOS_PASSWORD="your password" ; IONOSinventory.py

{
    "workbench": {
        "hosts": [
            "77.68.67.000"
        ],
        "vars": {}
    },
    "Center": {
        "hosts": [
            "77.68.67.000"
        ],
        "vars": {}
    },
    "_meta": {
        "hostvars": {
            "77.68.67.000": {
                "name": "workbench",
                "id": "10e4fb9f-1a89-4a06-8796-f77b3338cb3c"
            }
        }
    }
}
```

To use the IONOSinventory.py with Ansible with no options test it with the following command line:
```
$ ansible -i IONOSinventory.py -m ping all
```
To use it with the --dc option will be necessaery to create a bash script inventory.sh  like the following:
```
#!/bin/bash
./IONOSinventory.py --dc 4285791a-99a2-484d-804d-6e76bbdc7b84
```

And then execute it as inventory with Ansible:
```
$ ansible -i inventory.sh -m ping all
```
