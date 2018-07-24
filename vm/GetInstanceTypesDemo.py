#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.common.models.Filter import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.DescribeInstanceTypesRequest import *
import json

access_key = 'ak'
secret_key = 'sk'
regionId = 'cn-east-2'
azs = ['cn-east-2a', 'cn-east-2b']
instanceTypes = ['g.s1.small', 'g.s1.micro']
myFilter = []

filter_1 = Filter(name='instanceTypes', operator='eq', values=instanceTypes)
myFilter.append(filter_1)
filter_2 = Filter(name='az', operator='eq', values=azs)
myFilter.append(filter_2)

myParam = DescribeInstanceTypesParameters(regionId=regionId)
myParam.setFilters(myFilter)

myRequest = DescribeInstanceTypesRequest(parameters=myParam)

myCredential = Credential(access_key, secret_key)
myClient = VmClient(myCredential)

print 'Sending request...'
resp = myClient.send(myRequest)

for i in resp.result['instanceTypes']:
    print 'family: ', i['family']
    print 'instanceType: ', i['instanceType'], '\n'
# family:  g.s
# instanceType:  g.s1.micro
#
# family:  g.s
# instanceType:  g.s1.small
print json.dumps(resp.result,indent=2)
# {
#   "totalCount": 2,
#   "instanceTypes": [
#     {
#       "family": "g.s",
#       "cpu": 1,
#       "memoryMB": 1024,
#       "state": [
#         {
#           "az": "cn-east-2a",
#           "inStock": true
#         },
#         {
#           "az": "cn-east-2b",
#           "inStock": true
#         }
#       ],
#       "nicLimit": 2,
#       "instanceType": "g.s1.micro",
#       "desc": ""
#     },
#     {
#       "family": "g.s",
#       "cpu": 1,
#       "memoryMB": 2048,
#       "state": [
#         {
#           "az": "cn-east-2a",
#           "inStock": true
#         },
#         {
#           "az": "cn-east-2b",
#           "inStock": true
#         }
#       ],
#       "nicLimit": 2,
#       "instanceType": "g.s1.small",
#       "desc": ""
#     }
#   ],
#   "specificInstanceTypes": null
# }