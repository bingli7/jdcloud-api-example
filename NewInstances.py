#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vm.client.VmClient import VmClient
from jdcloud_sdk.services.vpc.models.NetworkInterfaceSpec import *
from jdcloud_sdk.services.vm.models.InstanceNetworkInterfaceAttachmentSpec import *
from jdcloud_sdk.services.charge.models.ChargeSpec import *
from jdcloud_sdk.services.disk.models.DiskSpec import *
from jdcloud_sdk.services.vm.models.InstanceDiskAttachmentSpec import *
from jdcloud_sdk.services.vpc.models.ElasticIpSpec import *
from jdcloud_sdk.services.vm.models.InstanceSpec import *
from jdcloud_sdk.services.vm.apis.CreateInstancesRequest import *


class NewInstances(object):

    def __init__(self, regionId, az, instanceType, imageId, name, password):
        self.regionId = regionId
        self.az = az
        self.instanceType = instanceType
        self.imageId = imageId
        self.name = name
        self.password = password
        self.dataDiskSpec = []
        print "Initiating finish..."

    def setUpClient(self, access_key, secret_key):
        my_access_key = access_key
        my_secret_key = secret_key
        self.credential = Credential(my_access_key, my_secret_key)
        self.client = VmClient(self.credential)
        print 'Client created...'

    def setNetworkSpec(self, subnetId, primaryIpAddress=None, securityGroups=None):
        new_networkinterface = NetworkInterfaceSpec(subnetId=subnetId, az=self.az, primaryIpAddress=primaryIpAddress, securityGroups=securityGroups)
        self.networkSpec = InstanceNetworkInterfaceAttachmentSpec(networkInterface=new_networkinterface)
        print 'NetworkSpec created...'
        print 'SubnetID: ' + self.networkSpec.networkInterface.subnetId

    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        self.chargeSpec = ChargeSpec(chargeMode, chargeUnit, chargeDuration)
        print 'ChargeSpec created...'
        print 'ChargeMode: ' + self.chargeSpec.chargeMode

    def setSystemDisk(self):
        self.systemDiskSpec = InstanceDiskAttachmentSpec(diskCategory='local')
        print 'SystemDiskSpec created...'
        print 'SystemDisk: ' + self.systemDiskSpec.diskCategory

    def setDataDisk(self, name, diskSizeGB, diskType, snapshotId=None):
        new_diskspec = DiskSpec(az=self.az, name=name, diskType=diskType, diskSizeGB=diskSizeGB, snapshotId=snapshotId)
        new_instanceDiskAttachmentSpec = InstanceDiskAttachmentSpec(diskCategory='cloud', cloudDiskSpec=new_diskspec)
        self.dataDiskSpec.append(new_instanceDiskAttachmentSpec)
        print 'DataDiskSpec created...'
        print 'DataDisk: ' + new_instanceDiskAttachmentSpec.diskCategory

    def setElasticIp(self, bandwidthMbps, provider, chargeSpec=None):
        self.elasticIpSpec = ElasticIpSpec(bandwidthMbps, provider, chargeSpec)
        print 'ElasticIPSpec created...'
        print 'BandWidth: ', self.elasticIpSpec.bandwidthMbps, '  provider: ', self.elasticIpSpec.provider

    def setDescription(self, description):
        self.description = description
        print 'Description created...'
        print 'Description: ' + self.description

    def setMaxCount(self, maxCount):
        self.maxCount = maxCount
        print 'MaxCount created...'
        print 'InstanceCount: ', self.maxCount

    def createInstances(self):

        print 'Creating instances...'

        self.instanceSpec = InstanceSpec(az=self.az, instanceType=self.instanceType, imageId=self.imageId, name=self.name, keyNames=None, primaryNetworkInterface=self.networkSpec, systemDisk=self.systemDiskSpec, dataDisks=self.dataDiskSpec, description=self.description, password=self.password, elasticIp=self.elasticIpSpec, charge=self.chargeSpec)
        print 'InstanceSpec created...'

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

        return resp


if __name__ == '__main__':

    regionId = 'cn-north-1'
    az = 'cn-north-1a'
    instanceType = 'g.s1.micro'
    instancename = 'pocenv-libing-apitest-0617'
    password = 'HelloWorld@618'
    imageId = '5de362a8-b5c7-4bc6-8b80-a7fab91475db'

    myinstances = NewInstances(regionId=regionId, az=az, instanceType=instanceType, imageId=imageId, name=instancename, password=password)

    access_key = 'ak'
    secret_key = 'sk'
    myinstances.setUpClient(access_key, secret_key)

    subnetId = 'subnet-pryeobh0fd'
    myinstances.setNetworkSpec(subnetId)

    chargeMode = 'postpaid_by_duration'
    myinstances.setChargeSpec(chargeMode)

    myinstances.setSystemDisk()

    dataDiskName = 'libing-test-'
    dataDiskSize = 30
    dataDiskType = 'premium-hdd'
    myinstances.setDataDisk(dataDiskName, dataDiskSize, dataDiskType)

    elasticIpBW = 3
    elasticIpprovider = 'bgp'
    myinstances.setElasticIp(elasticIpBW, elasticIpprovider)

    instanceDescription = 'libing testing API 0617'
    myinstances.setDescription(instanceDescription)

    instancesCount = 3
    myinstances.setMaxCount(instancesCount)

    myinstances.createInstances()