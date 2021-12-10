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


import socket
import sys
import requests
import json
import datetime
import base64
import os
from pprint import pprint
from getpass import getpass

###############################################
## You can configure username and password here
###############################################
#username=""
#password""
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

# If there are no Env Vars or no values from this file I am requesting User Inputs
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

#def findDatacentersDeep(authHead,hostNamed):
#  url = apiEp +"/datacenters?depth=5"
#  response = requests.get(url, headers=authHead)
#  datacentersRp = (response.json())
#  datacentersList = []
#  for item in datacentersRp['items']:
#    for lan in item['entities']['lans']['items']:
#        ciccio=lan['id']
#    for server in item['entities']['servers']['items']:
#      serverID = server['id']
#      hostNamedRp = server['properties']['name']
#      if hostNamedRp == hostNamed:
#        nicList=[]
#        counterNic=0
#        for nic in server['entities']['nics']['items']:
#            nicdict={}
#            id=nic['id']
#            nicName="eth" + str(counterNic)
#            nicdict["interface"]=nicName
#            macca=nic['properties']['mac']
#            nicdict["hardware_address"]=macca
#            netmasK="255.255.255.0"
#            nicdict["netmask"]=netmasK
#            Ip=nic['properties']['ips'][0]
#            nicdict["ip"]=Ip
#            nicList.append(nicdict)
#            counterNic=counterNic+1
#        # Create DictResponse
#        DictResponse = {}
#        DictResponse['network'] = nicList
#        return DictResponse
#      else:
#        continue

# Discontinued as I am not using --host anymore
#def findDatacentersDeep2(authHead,dcid,dcpvlan,hostReq):
#  url = apiEp +"/datacenters/" + dcid +"/servers?depth=3"
#  response = requests.get(url, headers=authHead)
#  serverRp = (response.json())
#  serverList=[]
#  for server in serverRp['items']:
#      serverDict = {}
#      srvId=server['id']
#      serverDict['srvid']=srvId
#      srvName=server['properties']['name']
#      if srvName != hostReq:
#        HNF="NotFound"
#        return  HNF
#        continue
#      else:
#        serverDict['name']=srvName
#        nics=server['entities']['nics']['items']
#        for nic in nics:
#            lan=str(nic['properties']['lan'])
#            if lan == dcpvlan:
#                srvIp=nic['properties']['ips'][0]
#                serverDict['ip']=srvIp
#        serverList.append(serverDict)
#      return serverList

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
          ip=srvr['ip']
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

#if whatToPrint == "HOST":
#      # Init Dicts
#    hostvarDict={}
#    hostvar={}
#    allprint={}
#    # Create DCs UUID list
#    dcs=findDatacenters(authAcc)
#    # Iterate inside DCs to find hosts 
#    for dc in dcs:
#        dcId=dc
#        dcName=findDatacentersName(authAcc,dc)
#        dcPvlan=findDatacentersPublicVlan(authAcc,dc)
##        serversDcList=listServers1DC(authAcc,dc,dcPvlan)
#        serversDcList=findDatacentersDeep2(authAcc,dc,dcPvlan,hostReq)
#        if serversDcList == "NotFound":
#              continue
#        srvrList=[]
#        srvrVars={}
#    # Build Dictionary of hostnames
#        for srvr in serversDcList:
#            ip=srvr['ip']
#            srvrList.append(ip)
#            srvname=srvr['name']
#            srvrVars["name"]=srvname
#            srvrid=srvr['srvid']
#            srvrVars["id"]=srvrid
#            hostvarDict[ip] = srvrVars
#        hostvar["hostvars"]=hostvarDict
#        allprint[srvname] = {"hosts": srvrList , 'vars': {}}
#        #print(allprint)
#    allprint["_meta"] = hostvar
#    allprint = json.dumps(allprint)
#    print(allprint)
