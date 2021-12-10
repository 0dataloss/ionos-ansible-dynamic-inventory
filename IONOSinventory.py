#!/usr/bin/env python3

# This file is part of Ansible,
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

######################################################################

import requests
import json
import base64
import os
from getpass import getpass

###############################################
## You can configure username and password here
###############################################
username=""
password=""
###############################################
# Read Env Variables 
if os.getenv('IONOS_USERNAME'):
    username = os.getenv('IONOS_USERNAME')
if os.getenv('IONOS_PASSWORD'):
    password = os.getenv('IONOS_PASSWORD')

# Initial vars
whatToPrint="LIST"
apiEp="https://api.ionos.com/cloudapi/v6"

# Manage selector but it can be done better than this, I am sure
''' Disabling Filters
if len(sys.argv) > 1:
  whatToPrint = "LIST"
if len(sys.argv) > 2:
  # --host is discontinued all is provided with --list
  if sys.argv[1] == "--host":
    hostReq = sys.argv[2]
    whatToPrint = "LIST" 
  else:
    if sys.argv[1] == "--list":
      whatToPrint = "LIST"
'''

# If there are no Env Vars or no file configuration I am requesting User Inputs
if isinstance(username,str):
  user_input_username = username
else:
  user_input_username = input("Please insert username\n")
if isinstance(password,str):
  user_input_password=password
else:
  user_input_password=getpass()
# End User Input

# Prepare base64 username:password Header
user_input_usernameandpassword=str(user_input_username+":"+user_input_password)
message_bytes = user_input_usernameandpassword.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
token = base64_bytes.decode('ascii')
authAcc={"Authorization": "Basic "+token+""}

# Build a List of product which have been used per DC
def findDatacenters(authHead):
  url = apiEp +"/datacenters?depth=0"
  response = requests.get(url, headers=authHead)
  datacentersRp = (response.json())
  datacentersList = []
  datacentersRp = datacentersRp['items']
  for uuid in datacentersRp:
    uuid = uuid['id']
    datacentersList.append(uuid)
  return datacentersList

def findDatacentersName(authHead,dc):
  url = apiEp +"/datacenters/"+dc+"?depth=1"
  response = requests.get(url, headers=authHead)
  datacentersRp = (response.json())
  name = datacentersRp['properties']['name']
  return name

def findDatacentersPublicVlan(authHead,dc):
  url = apiEp +"/datacenters/"+dc+"?depth=5"
  response = requests.get(url, headers=authHead)
  datacentersRp = (response.json())
  lans = datacentersRp['entities']['lans']['items']
  for lan in lans:
      lanId=lan['id']
      isPublic=lan['properties']['public']
      if isPublic is True:
          return lanId
# Placeholder for DC with no public VLANS
#      else:
#          lanNotPublic=True
#          return lanNotPublic

def listServers1DC(authHead,dcid,dcpvlan):
  url = apiEp +"/datacenters/" + dcid +"/servers?depth=3"
  response = requests.get(url, headers=authHead)
  serverRp = (response.json())
  serverList=[]
  for server in serverRp['items']:
      serverDict = {}
      srvId=server['id']
      serverDict['srvid']=srvId
      srvName=server['properties']['name']
      serverDict['name']=srvName
      nics=server['entities']['nics']['items']
      if str(dcpvlan) == "000":
        print("I am here!!!!")
        serverDict['ip']="No Public Connection"
      else:
        for nic in nics:
          lan=str(nic['properties']['lan'])
          if lan == dcpvlan:
              srvIp=nic['properties']['ips'][0]
              serverDict['ip']=srvIp
      serverList.append(serverDict)
  return serverList


if whatToPrint == "LIST":      
    # Init Dicts
    hostvarDict={}
    hostvar={}
    allprint={}
    # Create DCs UUID list
    dcs=findDatacenters(authAcc)
    # Iterate inside DCs to find all the hosts 
    for dc in dcs:
        dcId=dc
        dcName=findDatacentersName(authAcc,dc)
        dcPvlan=findDatacentersPublicVlan(authAcc,dc)
        serversDcList=listServers1DC(authAcc,dc,dcPvlan)
        srvrList=[]
    # Build Dictionary of hostnames and DataCenters
        for srvr in serversDcList:
          srvrPip=[]
          srvrVars={}
          # If Instance does not have Public IP returns NULL
          ip=srvr.get('ip')
          srvrList.append(ip)
          srvrPip.append(ip)
          srvname=srvr['name']
          srvrVars["name"]=srvname
          srvrid=srvr['srvid']
          srvrVars["id"]=srvrid
          hostvarDict[ip] = srvrVars
          allprint[srvname] = {"hosts": srvrPip , 'vars': {}}
        hostvar["hostvars"]=hostvarDict
        allprint[dcName] = {"hosts": srvrList , 'vars': {}}
        #print(allprint)
    allprint["_meta"] = hostvar
    allprint = json.dumps(allprint)
    print(allprint)