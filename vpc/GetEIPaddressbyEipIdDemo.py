#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vpc.client.VpcClient import *
from jdcloud_sdk.services.common.models.Filter import *
from jdcloud_sdk.services.vpc.apis.DescribeElasticIpsRequest import *
import json

access_key = 'ak'
secret_key = 'sk'
regionId = 'cn-north-1'

myCredential = Credential(access_key, secret_key)
myClient = VpcClient(myCredential)

# List of all the EIP IDs
eipList = ['fip-tj98zpg0ym', 'fip-0rsd6husd2', 'fip-7quu2vwtmu']

# Filter by EIP ID
myFilter = Filter('elasticIpIds', eipList)
myParam = DescribeElasticIpsParameters(regionId)
myParam.setFilters([myFilter])
myRequest = DescribeElasticIpsRequest(myParam)

resp = myClient.send(myRequest)
# output all the info of EIPs
print json.dumps(resp.result, indent=2)

eipID = []
# get the public IPs by order
for elasticIp in resp.result['elasticIps']:
    eipID.append(elasticIp['elasticIpAddress'].encode('utf-8'))

print eipID