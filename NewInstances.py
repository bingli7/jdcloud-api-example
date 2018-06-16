#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jdcloud_sdk.core import VmClient, Credential
from jdcloud_sdk.services.vm.models.InstanceDiskAttachmentSpec import *
from jdcloud_sdk.services.vpc.models.NetworkInterfaceSpec import *
from jdcloud_sdk.services.vm.models.InstanceNetworkInterfaceAttachmentSpec import *
from jdcloud_sdk.services.charge.models.ChargeSpec import *
from jdcloud_sdk.services.disk.models.DiskSpec import *
from jdcloud_sdk.services.vm.models.InstanceDiskAttachmentSpec import *
from jdcloud_sdk.services.vpc.models.ElasticIpSpec import *
from jdcloud_sdk.services.vm.models.InstanceSpec import *
from jdcloud_sdk.services.vm.apis.CreateInstancesRequest import *

class NewInstances(object):

    def __init__(self, regionId, az, instanceType, imageId，name, password, count):
        self.regionId = regionId
        self.az = az
        self.instanceType = instanceType
        self.imageId = imageId
        self.name = name
        self.password = password
        self.count = count
        self.dataDiskSpec = []

    def setUpClient(self, access_key, secret_key):
        my_access_key = access_key
        my_secret_key = secret_key
        self.credential = Credential(my_access_key, my_secret_key)
        self.client = VmClient(self.credential)


    def setNetworkSpec(self, subnetId, primaryIpAddress=None, securityGroups=None):
        new_networkinterface = NetworkInterfaceSpec(subnetId=subnetId, az=self.az, primaryIpAddress=primaryIpAddress, \
            securityGroups=securityGroups)
        self.networkSpec = InstanceNetworkInterfaceAttachmentSpec(new_networkinterface)


    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        self.chargeSpec = ChargeSpec(chargeMode, chargeUnit, chargeDuration)


    def setSystemDisk(self):
        self.systemDiskSpec = InstanceDiskAttachmentSpec(diskCategory='local')


    def setDataDisk(self, name, diskSizeGB, diskType, snapshotId=None):
        new_diskspec = DiskSpec(az=self.az, name=name, diskType=diskType, \
            diskSizeGB=diskSizeGB, snapshotId=snapshotId)
        self.dataDiskSpec.append(InstanceDiskAttachmentSpec(diskCategory='cloud', cloudDiskSpec=new_diskspec))

        
    def setElasticIp(self, bandwidthMbps, provider, chargeSpec=None):
        self.elasticIpSpec = ElasticIpSpec(bandwidthMbps, provider, chargeSpec)


    def setDescription(self, description):
        self.description = description

    def setMaxCount(self, maxCount):
        self.maxCount = maxCount


    def createInstances(self):
        self.instanceSpec = InstanceSpec(az=self.az, instanceType=self.instanceType, imageId=self.imageId, \
            name=self.name, password=self.password, primaryNetworkInterface=self.networkSpec, \
            systemDisk=self.systemDiskSpec, dataDisks=self.dataDiskSpec, description=self.description, \
            elasticIp=self.elasticIpSpec, charge=self.chargeSpec)

        # Create Instance Parameters
        self.newParam = CreateInstancesParameters(self.regionId)
        self.newParam.setInstanceSpec(self.instanceSpec)
        self.newParam.setMaxCount(self.maxCount)

        # Create Request
        self.newRequest = CreateInstancesRequest(self.newParam)

        # Client send request
        resp = self.client.send(self.newRequest)

        if resp.error is not None:
            print resp.error.code, resp.error.message  


if __name__ == '__main__':
    pass