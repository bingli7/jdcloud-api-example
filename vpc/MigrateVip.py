#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vm.client.VmClient import VmClient
from jdcloud_sdk.services.vm.apis.AttachNetworkInterfaceRequest import *
from jdcloud_sdk.services.vm.apis.DetachNetworkInterfaceRequest import *
from jdcloud_sdk.services.vm.apis.DescribeInstanceRequest import *
import logging
import sys

# ak & sk
access_key = 'ak'
secret_key = 'sk'
# 区域resion id
region_id = 'cn-north-1'
# 弹性网卡ID
ENI = 'port-ejuyeng7qs'
# 本实例ID
thisVmId = 'i-3ltkvzycml'
# 对方实例ID
thatVmId = 'i-yupwhaqzet'

myCredential = Credential(access_key, secret_key)
myClient = VmClient(myCredential)

# 日志输出至/etc/keepalived/keepalived.log
logger = logging.getLogger("KeepAlived")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
# 输出到文件pgy.log
file_handler = logging.FileHandler("keepalived.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def attach_eni(instanceId, networkInterfaceId):
    logger.info('Trying to attach elastic NI to ' + instanceId)
    try:
        parameters = AttachNetworkInterfaceParameters(instanceId=instanceId, regionId=region_id, \
                                                      networkInterfaceId=networkInterfaceId)
        request = AttachNetworkInterfaceRequest(parameters)
        resp = myClient.send(request)
        if resp.error is not None:
            logger.error('Fail to attach elastic NI to instance: ' + instanceId)
            logger.error(str(resp.error.code) + ': ' + resp.error.message)
            sys.exit('error to attach!')
        else:
            logger.info('Succeed to attach elastic NI to instance: ' + instanceId)
    except Exception, e:
        logger.error('Fail to attach elastic NI to instance: ' + instanceId)
        sys.exit('error to attach!')

def detach_eni(instanceId, networkInterfaceId):
    logger.info('Trying to detach elastic NI from instance: ' + instanceId)
    try:
        parameters = DetachNetworkInterfaceParameters(instanceId=instanceId, regionId=region_id, \
                                                      networkInterfaceId=networkInterfaceId)
        request = DetachNetworkInterfaceRequest(parameters)
        resp = myClient.send(request)
        if resp.error is not None:
            logger.error('Fail to detach elastic NI from instance: ' + instanceId)
            logger.error(str(resp.error.code) + ': ' + resp.error.message)
            sys.exit('error to detach!')
        else:
            logger.info('Succeed to detach elastic NI from instance: ' + instanceId)
    except Exception, e:
        logger.error('Fail to detach elastic NI from instance: ' + instanceId)
        sys.exit('error to detach!')

def check_attach(instanceId):
    try:
        parameters = DescribeInstanceParameters(region_id, instanceId)
        request = DescribeInstanceRequest(parameters)
        resp = myClient.send(request)
        if resp.error is not None:
            logger.error('Fail to check instance\'s status: ' + instanceId)
            logger.error(str(resp.error.code) + ': ' + resp.error.message)
            sys.exit('error to check instance!')
        else:
            return resp.result['instance'].has_key('secondaryNetworkInterfaces')
    except Exception, e:
        logger.error('Fail to check instance\'s status: ' + instanceId)
        sys.exit('error to check instance!')

logger.info('Migrate Elastic Network Interface...')
detach_eni(thatVmId, ENI)
while check_attach(thatVmId):
    logger.info('waiting for detach...')
    continue
attach_eni(thisVmId, ENI)
