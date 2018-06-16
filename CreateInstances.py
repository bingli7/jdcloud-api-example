#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jdcloud_sdk.core import VmClient, Credential
from jdcloud_sdk.services.vm.models import InstanceDiskAttachmentSpec

class NewInstances(object):

    def __init__(self, az, instanceType, imageId，name, password, count):
        self.az = az
        self.instanceType = instanceType
        self.imageId = imageId
        self.name = name
        self.password = password
        self.count = count

    def setUpClient(self, access_key, secret_key):
        my_access_key = access_key
        my_secret_key = secret_key
        self.credential = Credential(my_access_key, my_secret_key)
        self.client = VmClient(self.credential)


    def setNetworkSpec(self, subnetId, primaryIpAddress=None, securityGroups=None):
        pass


    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        pass

    def setSystemDisk(self):
        return InstanceDiskAttachmentSpec('local')

    def setDataDisk(self):
        pass

    def setElasticIp(self):
        pass


if __name__ == '__main__':
    pass