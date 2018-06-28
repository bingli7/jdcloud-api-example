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

# ip address in a list, Only 1 IP address can be accepted once
ipList = ['116.196.108.44']

# filter by EIP address
newFilter = Filter(name='elasticIpAddress', values=ipList)

myParam = DescribeElasticIpsParameters(regionId)
myParam.setFilters([newFilter])
myRequest = DescribeElasticIpsRequest(myParam)

resp = myClient.send(myRequest)

print json.dumps(resp.result, indent=2)

# get the EIP id from the response: fip-tj98zpg0ym
myEipID = resp.result['elasticIps'][0]['elasticIpId']