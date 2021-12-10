# Dynamic Inventory

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Test your setup](#testyoursetup)

## Description

IONOSinventory.py is an Ansible dynamic inventory, able to generate JSON output from requests sent to the using n external inventory system that can generate a proper JSON output from the Ionos API infrastructure.

## Installation

No special install procedure is required. 
The script can be used standalone or with Ansible
The IONOSinventory.py has been tested with Python 3.8

## Configuration

To use the scrip is recommended to export your IONOS credential for a user with admin access as environment variables:
```
export IONOS_USERNAME="your@username.com" && export IONOS_PASSWORD="your password"
```
or
Is possible to specify username and password inside the file itself (recommended ONLY for dev purposes)
```
###############################################
## You can configure username and password here
###############################################
username=0
password0
###############################################
```
or
If none of the two options above have been set-up, the script will request user iniput username and password.

It is also possible to change the api end-point URL; there is no need right now as the script has been design for the latest version of the API end-point (v6.0), and this functionality is reserved for future use.
```
apiEp="https://api.ionos.com/cloudapi/v6"
```

## Usage

IONOSinventory.py exposes bi default the `--list` functionality required by the Ansible inventory system; the `--list` switch is the only one implemented so far.

In this mode, the IONOSinventory.py will expose servers grouped by Virtual Data Center and by Name.
At this moment there is an issue with the 'grouped by name' as if there are multiple machines with the same name across multiple Virtual Data Center they will all be used as 'host' by Ansible.

## Test your setup
Is it possible to run the script standalone against the IONOS API to verify if the username and password used
are working as expected in terms of accessing resources

```
$ export IONOS_USERNAME="your@username.com" && export IONOS_PASSWORD="your password" ; inventory.py 

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