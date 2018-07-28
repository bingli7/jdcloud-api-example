#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.DescribeInstanceVncUrlRequest import *
import sys

# ak & sk
access_key = '<ak>'
secret_key = '<sk>'

regionId = 'cn-north-1'
instanceId = 'i-93mgkfsdhv'

myParam = DescribeInstanceVncUrlParameters(regionId, instanceId)
myRequest = DescribeInstanceVncUrlRequest(myParam)
myCredential = Credential(access_key, secret_key)
myClient = VmClient(myCredential)

try:
    resp = myClient.send(myRequest)
    if resp.error is not None:
        print (resp.error.message)
    print resp.result['vncUrl'].encode('utf-8')
except Exception, e:
    print e
    sys.exit('error! 获取Vnc Url失败！')