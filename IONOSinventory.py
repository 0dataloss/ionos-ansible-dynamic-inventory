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
import sys
from getpass import getpass

#################################################
## You can configure username and password here##
#################################################
#username=""
#password=""
#################################################
try:
  username
except:
  username=None
try:
  password
except:
  password=None

###############################################
# Read Env Variables 
if os.getenv('IONOS_USERNAME'):
    username = os.getenv('IONOS_USERNAME')
if os.getenv('IONOS_PASSWORD'):
    password = os.getenv('IONOS_PASSWORD')

# Initial vars if there are no arguments
whatToPrint="LIST"
apiEp="https://api.ionos.com/cloudapi/v6"

# Manage selector but it can be done better than this, I am sure
if len(sys.argv) == 2:
  if sys.argv[1] == "--help":
    print(f"\n{sys.argv[0]} is a Python script designed to work with Ansible as dynamic inventory.\n\nUSAGE:\n"
    f"  {sys.argv[0]} [flag]\n\n"
    f"FLAGS:\n"
    f"  --dc               retrieve a list of UUID and VDC Names\n"
    f"  --dc <UUID>        list all the servers inside a specivif VDC\n"
    f"  --off              retrieve a list of server in status SHUTOFF\n"
    f"  --off --dc <UUID>  returns a list of servers in status SHUTOFF for a specific VDC\n")
    sys.exit(0)
  if sys.argv[1] == "--list":
    whatToPrint = "LIST"
  elif sys.argv[1] == "--off":
    whatToPrint = "SHUTOFF"
  elif sys.argv[1] == "--dc":
    whatToPrint = "DCLIST"
  else:
    print(f"\n{sys.argv[0]} is a Python script designed to work with Ansible as dynamic inventory.\n\nUSAGE:\n"
    f"  {sys.argv[0]} [flag]\n\n"
    f"FLAGS:\n"
    f"  --dc               retrieve a list of UUID and VDC Names\n"
    f"  --dc <UUID>        list all the servers inside a specivif VDC\n"
    f"  --off              retrieve a list of server in status SHUTOFF\n"
    f"  --off --dc <UUID>  returns a list of servers in status SHUTOFF for a specific VDC\n")
    sys.exit(1)
elif len(sys.argv) == 3 :
  if sys.argv[1] == "--dc":
    dcUuid=sys.argv[2]
    try:
      dcUuid
      whatToPrint = "DC"
    except:
      print(f"with the flag --dc you have to specify a VDC UUID")
      sys.exit(1)
elif len(sys.argv) == 4 :
  if sys.argv[1] == "--dc":
    dcUuid=sys.argv[2]
    try:
      dcUuid
    except:
      print(f"with the flag --dc you have to specify a VDC UUID")
      sys.exit(1)
    if sys.argv[3] == "--off":
      whatToPrint = "OFFDC"
  elif sys.argv[1] == "--off":
    if sys.argv[2] == "--dc":
      dcUuid=sys.argv[3]
    try:
      dcUuid
      whatToPrint = "OFFDC"
    except:
      print(f"with the flag --dc you have to specify a VDC UUID")
      sys.exit(1)

# If there are no Env Vars or no file configuration I am requesting User Inputs
# IT DOES NOT WORK IF YOU CALL THE INVENTORY WITH 'ansible -i IONOSinventory.py'
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
  publicLanList=[]
  for lan in lans:
    lanId=lan['id']
    lanName=lan['properties']['name']
    isPublic=lan['properties']['public']
    # Filter K8S node servers because is a PaaS not a IaaS
    if lanName != "k8s-public-lan":
      if isPublic is True:
        publicLanList.append(lanId)
  return publicLanList
#########################################
# Placeholder for DC with no public VLANS
#########################################
#      else:
#          lanNotPublic=True
#          return lanNotPublic

def listServers1DC(authHead,dcid,dcpvlan,reqstatus):
  url = apiEp +"/datacenters/" + dcid +"/servers?depth=3"
  response = requests.get(url, headers=authHead)
  serverRp = (response.json())
  serverList=[]
  for server in serverRp['items']:
      serverDict = {}
      srvId=server['id']
      serverDict['srvid']=srvId
      srvName=server['properties']['name']
      srvStatus=server['properties']['vmState']
      serverDict['name']=srvName
      nics=server['entities']['nics']['items']
      for nic in nics:
        lan=str(nic['properties']['lan'])
        for i in dcpvlan:
          if lan == i:
            if srvStatus == reqstatus:
              if reqstatus == "RUNNING":
                srvIp=nic['properties']['ips'][0]
                serverDict['ip']=srvIp
                serverList.append(serverDict)
              else:
                serverDict['ip']="No IP Assigned"
                serverList.append(serverDict)
  return serverList

def printlist(authAcc,reqstatus):
  # Init Dicts
  hostvarDict={}
  hostvar={}
  allprint={}
  # Create DCs UUID list
  dcs=findDatacenters(authAcc)
  # Iterate inside DCs to find all the hosts 
  if reqstatus == "DCLIST":
    for dc in dcs:
      dcName=findDatacentersName(authAcc,dc)
      allprint[dc]=dcName
    return allprint
  for dc in dcs:
      c0=0
      dcName=findDatacentersName(authAcc,dc)
      dcPvlan=findDatacentersPublicVlan(authAcc,dc)
      serversDcList=listServers1DC(authAcc,dc,dcPvlan,reqstatus)
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
        hostvarDict[c0] = srvrVars
        allprint[srvname] = {"hosts": srvrPip , 'vars': {}}
        c0=(c0+1)
      hostvar["hostvars"]=hostvarDict
      allprint[dcName] = {"hosts": srvrList , 'vars': {}}
  allprint["_meta"] = hostvar
  allprint = json.dumps(allprint)
  return allprint

# MAIN
# Print Servers RUNNING with public interface for all VDC
if whatToPrint == "LIST":
  allprint=printlist(authAcc,"RUNNING")
  print(allprint)
# Print Servers SHUTOFF with public interface for all VDC
elif whatToPrint == "SHUTOFF":
  allprint=printlist(authAcc,"SHUTOFF")
  print(allprint)
# Print Servers RUNNING with public interface for 1 VDC 
elif whatToPrint == "DCLIST":
  allprint=printlist(authAcc,"DCLIST")
  print(allprint)
elif whatToPrint == "DC" :
  reqstatus="RUNNING"
  dcPvlan=findDatacentersPublicVlan(authAcc,dcUuid)
  serversDcList=listServers1DC(authAcc,dcUuid,dcPvlan,reqstatus)
  srvrList=[]
  # Build Dictionary of hostnames and DataCenters
  # Init Dicts
  hostvarDict={}
  hostvar={}
  allprint={}
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
  allprint[dcUuid] = {"hosts": srvrList , 'vars': {}}
  allprint["_meta"] = hostvar
  allprint = json.dumps(allprint)
  print(allprint)
# Print servers SHUTOFF with public interface for 1 single VDC
elif whatToPrint == "OFFDC":
  dcPvlan=findDatacentersPublicVlan(authAcc,dcUuid)
  serversDcList=listServers1DC(authAcc,dcUuid,dcPvlan,"SHUTOFF")
  srvrList=[]
  # Build Dictionary of hostnames and DataCenters
  # Init Dicts
  hostvarDict={}
  hostvar={}
  allprint={}
  c0=0
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
    hostvarDict[c0] = srvrVars
    allprint[srvname] = {"hosts": srvrPip , 'vars': {}}
    c0=(c0+1)
  hostvar["hostvars"]=hostvarDict
  allprint[dcUuid] = {"hosts": srvrList , 'vars': {}}
  allprint["_meta"] = hostvar
  allprint = json.dumps(allprint)
  print(allprint)


