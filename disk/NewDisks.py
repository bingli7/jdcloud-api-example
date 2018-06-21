#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.disk.client.DiskClient import DiskClient
from jdcloud_sdk.services.disk.models.DiskSpec import DiskSpec
from jdcloud_sdk.services.disk.apis.CreateDisksRequest import *
from jdcloud_sdk.services.charge.models.ChargeSpec import *
import uuid

class NewDisks(object):
    '''
    Create 1 or more disks
    '''
    def __init__(self, access_key, secret_key, regionId, az, name, diskType,\
                 diskSizeGB, description=None, snapshotId=None, chargeSpec=None, maxCount=1):

        self.regionId = regionId
        self.az = az
        self.name = name
        # ssd or premium-hdd
        self.diskType = diskType
        # diskSizeGB: type of Integer
        self.diskSizeGB = diskSizeGB
        self.description = description
        self.snapshotId = snapshotId
        #        :param chargeMode: (Optional) 计费模式，取值为：prepaid_by_duration，postpaid_by_usage或postpaid_by_duration，prepaid_by_duration表示预付费，postpaid_by_usage表示按用量后付费，postpaid_by_duration表示按配置后付费，默认为postpaid_by_duration
        self.chargeSpec = chargeSpec
        self.maxCount = maxCount

        self.credential = Credential(access_key, secret_key)
        self.client = DiskClient(self.credential)
        print 'Client created...'

    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        # chargeMode:  prepaid_by_duration:预付费，postpaid_by_usage:按用量后付费，postpaid_by_duration:按配置后付费，默认为postpaid_by_duration
        self.chargeSpec = ChargeSpec(chargeMode, chargeUnit, chargeDuration)
        print 'ChargeSpec created...'
        print 'ChargeMode: ' + self.chargeSpec.chargeMode

    def createDisks(self):
        # Create Disks and get the response
        # Return list: str[]
        clientToken = str(uuid.uuid4())[:5]
        myDiskSpec = DiskSpec(az=self.az, name=self.name, diskType=self.diskType, diskSizeGB=self.diskSizeGB,\
                               description=self.description, snapshotId=self.snapshotId, charge=self.chargeSpec)
        myParam = CreateDisksParameters(regionId=self.regionId, diskSpec=myDiskSpec,\
                                        maxCount=self.maxCount, clientToken=clientToken)
        myRequest = CreateDisksRequest(parameters=myParam)

        resp = self.client.send(myRequest)

        if resp.error is not None:
            print resp.error.code, resp.error.message

        my_resp = []
        # from unicode to utf8
        for i in resp.result['diskIds']:
            my_resp.append(i.encode("utf-8"))

        return my_resp

if __name__ == '__main__':
    access_key = 'ak'
    secret_key = 'sk'
    regionId = 'cn-north-1'
    az = 'cn-north-1a'
    name = 'libing-apitest-0620'
    diskType = 'ssd'
    diskSizeGB = 20
    description = "libing is testing Disk OpenAPI"
    maxCount = 3

    myDisks = NewDisks(access_key=access_key, secret_key=secret_key, regionId=regionId,\
                       az=az, name=name, diskType=diskType, diskSizeGB=diskSizeGB,\
                       description=description, maxCount=maxCount)

    chargeMode = 'postpaid_by_duration'
    myDisks.setChargeSpec(chargeMode=chargeMode)

    resp = myDisks.createDisks()

    print resp
    # ['vol-23zsdfrm0s', 'vol-grtpo55vz0', 'vol-122nsdvon4']
