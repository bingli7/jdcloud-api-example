#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.disk.client.DiskClient import DiskClient
from jdcloud_sdk.services.disk.models.DiskSpec import DiskSpec
from jdcloud_sdk.services.disk.apis.CreateDisksRequest import *
import uuid

class NewDisks(object):
    '''
    Create 1 or more disks
    '''
    def __init__(self, access_key, secret_key, regionId, az, name, diskType,\
                 diskSizeGB, description=None, snapshotId=None, charge=None, maxCount=1):
        # your access key and private secret key
        my_access_key = access_key
        my_secret_key = secret_key
        self.regionId = regionId
        self.az = az
        self.name = name
        # ssd or premium-hdd
        self.diskType = diskType
        # diskSizeGB: type of Integer
        self.diskSizeGB = diskSizeGB
        self.description = description
        self.snapshotId = snapshotId
        self.charge = charge
        self.maxCount = maxCount

        self.credential = Credential(my_access_key, my_secret_key)
        self.client = DiskClient(self.credential)
        print 'Client created...'

    def createDisks(self):
        # Create Disks and get the response
        # Return list: str[]
        clientToken = str(uuid.uuid4())[:5]
        myDiskSpec = DiskSpec(az=self.az, name=self.name, diskType=self.diskType, diskSizeGB=self.diskSizeGB,\
                               description=self.description, snapshotId=self.snapshotId, charge=self.charge)
        myParam = CreateDisksParameters(regionId=self.regionId, diskSpec=myDiskSpec,\
                                        maxCount=self.maxCount, clientToken=clientToken)
        myRequest = CreateDisksRequest(parameters=myParam)

        myResp = self.client.send(myRequest)

        if myResp.error is not None:
            print myResp.error.code, myResp.error.message

        my_resp = []
        # from unicode to utf8
        for i in myResp.result['diskIds']:
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

    resp = myDisks.createDisks()

    print resp
    # ['vol-23zsdfrm0s', 'vol-grtpo55vz0', 'vol-122nsdvon4']
