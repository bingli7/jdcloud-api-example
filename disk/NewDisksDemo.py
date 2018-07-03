#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.services.disk.client.DiskClient import *
from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.charge.models.ChargeSpec import *
from jdcloud_sdk.services.disk.models.DiskSpec import *
from jdcloud_sdk.services.disk.apis.CreateDisksRequest import *
import uuid
import json

# ak & sk
access_key = '<ak>'
secret_key = '<sk>'
# 区域
regionId = 'cn-north-1'
# 可用区
az = 'cn-north-1a'
# 云盘name前缀
namePrefix = 'libing-disk'
# 云盘类型：ssd/premium-hdd
type = 'ssd'
# 描述
description = 'SSD Disk testing'
# 云盘大小（GiB）
size = 20
# 创建云硬盘数量
count = 2
# clientToken：短随机数
clientToken = str(uuid.uuid4())[:5]
# 计费模式：按配置后付费
chargeMode = 'postpaid_by_duration'
myChargeSpec = ChargeSpec(chargeMode=chargeMode)
# Disk spec
myDiskSpec = DiskSpec(az=az, name=namePrefix, diskType=type, diskSizeGB=size, description=description, charge=myChargeSpec)
myParam = CreateDisksParameters(regionId=regionId, diskSpec=myDiskSpec, maxCount=count, clientToken=clientToken)
myRequest = CreateDisksRequest(myParam)

myCredential = Credential(access_key, secret_key)
myClient = DiskClient(myCredential)
# 发送创建云盘请求
resp = myClient.send(myRequest)

print json.dumps(resp.result, indent=2)

diskIds = []
for i in resp.result['diskIds']:
    diskIds.append(i.encode('utf-8'))
print 'Disk IDs: ', diskIds