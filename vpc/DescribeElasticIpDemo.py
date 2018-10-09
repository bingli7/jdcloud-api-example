#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.vpc.client.VpcClient import *
from jdcloud_sdk.services.vpc.apis.DescribeElasticIpRequest import *


access_key = 'ak'
secret_key = 'sk'
regionId = 'cn-north-1'

elasticIpId = 'fip-b6w3jfo9dj'

myCredential = Credential(access_key, secret_key)
myClient = VpcClient(myCredential)

myParam = DescribeElasticIpParameters(regionId=regionId, elasticIpId=elasticIpId)

myRequest = DescribeElasticIpRequest(myParam)

resp = myClient.send(myRequest)

print resp