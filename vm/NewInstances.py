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

    def __init__(self, access_key, secret_key, regionId, az, instanceType, imageId,\
                 name, password, maxCount=1, chargeSpec=None, description=None):
        self.regionId = regionId
        self.az = az
        # E.G. 'g.s1.micro'
        self.instanceType = instanceType
        self.imageId = imageId
        # instance name prefix
        self.name = name
        self.password = password
        self.maxCount = maxCount
        # Default None: postpaid_by_duration:按配置后付费
        self.chargeSpec = chargeSpec
        self.description = description
        # InstanceDiskAttachmentSpec[]
        self.dataDiskSpec = []

        self.elasticIpSpec = None

        self.credential = Credential(access_key, secret_key)
        self.client = VmClient(self.credential)
        print 'Client created...'

    def setNetworkSpec(self, subnetId, primaryIpAddress=None, securityGroups=None):
        # Necessary: subnetID   Optional: primaryIpAddress/securityGroups
        new_networkinterface = NetworkInterfaceSpec(subnetId=subnetId, az=self.az, primaryIpAddress=primaryIpAddress,\
                                                    securityGroups=securityGroups)
        self.networkSpec = InstanceNetworkInterfaceAttachmentSpec(networkInterface=new_networkinterface)
        print 'NetworkSpec created...'
        print 'SubnetID: ' + self.networkSpec.networkInterface.subnetId

    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        # chargeMode:   prepaid_by_duration:预付费，postpaid_by_usage:按用量后付费，postpaid_by_duration:按配置后付费，默认为postpaid_by_duration
        self.chargeSpec = ChargeSpec(chargeMode, chargeUnit, chargeDuration)
        print 'ChargeSpec created...'
        print 'ChargeMode: ' + self.chargeSpec.chargeMode

    def setSystemDisk(self):
        # System disk: diskCategory='local'
        self.systemDiskSpec = InstanceDiskAttachmentSpec(diskCategory='local')
        print 'SystemDiskSpec created...'
        print 'SystemDisk: ' + self.systemDiskSpec.diskCategory

    def setDataDisk(self, name, diskSizeGB, diskType, snapshotId=None):
        # Data disk: diskCategory='cloud'
        new_diskspec = DiskSpec(az=self.az, name=name, diskType=diskType, diskSizeGB=diskSizeGB, snapshotId=snapshotId)
        new_instanceDiskAttachmentSpec = InstanceDiskAttachmentSpec(diskCategory='cloud', cloudDiskSpec=new_diskspec)
        self.dataDiskSpec.append(new_instanceDiskAttachmentSpec)
        print 'DataDiskSpec created...'
        print 'DataDisk: ' + new_instanceDiskAttachmentSpec.diskCategory

    def setElasticIp(self, bandwidthMbps, provider):
        #  bandwidthMbps(Integer), provider: 'bgp' or 'no_bgp'
        self.elasticIpSpec = ElasticIpSpec(bandwidthMbps, provider, self.chargeSpec)
        print 'ElasticIPSpec created...'
        print 'BandWidth: ', self.elasticIpSpec.bandwidthMbps, '  provider: ', self.elasticIpSpec.provider

    def createInstances(self):
        # Create instances and get the response
        # Return list: str[]
        print 'Creating instances...'
        instanceSpec = InstanceSpec(az=self.az, instanceType=self.instanceType, imageId=self.imageId,\
                                         name=self.name, keyNames=None, primaryNetworkInterface=self.networkSpec,\
                                         systemDisk=self.systemDiskSpec, dataDisks=self.dataDiskSpec, description=self.description,\
                                         password=self.password, elasticIp=self.elasticIpSpec, charge=self.chargeSpec)

        # Create Instance Parameters
        newParam = CreateInstancesParameters(self.regionId)
        newParam.setInstanceSpec(instanceSpec)
        newParam.setMaxCount(self.maxCount)
        # Create Request
        newRequest = CreateInstancesRequest(newParam)

        # Client send request
        resp = self.client.send(newRequest)

        if resp.error is not None:
            print resp.error.code, resp.error.message

        my_resp = []
        #from unicode to utf8
        for i in resp.result['instanceIds']:
            my_resp.append(i.encode("utf-8"))

        return my_resp

if __name__ == '__main__':
    # parameters:
    regionId = 'cn-north-1'
    az = 'cn-north-1a'
    instanceType = 'g.s1.micro'
    instancename = 'pocenv-libing-apitest-0620-'
    password = 'HelloWorld@618'
    imageId = '5de362a8-b5c7-4bc6-8b80-a7fab91475db'
    access_key = 'ak'
    secret_key = 'sk'
    maxCount = 2
    description = "libing testing 20180620"
    myinstances = NewInstances(access_key=access_key, secret_key=secret_key,regionId=regionId,\
                               az=az, instanceType=instanceType, imageId=imageId,\
                               name=instancename, password=password, maxCount=maxCount,\
                               description=description)

    # Set up charge spec
    chargeMode = 'postpaid_by_duration'
    myinstances.setChargeSpec(chargeMode=chargeMode)
    # Set up network
    subnetId = 'subnet-pryeobh0fd'
    myinstances.setNetworkSpec(subnetId)
    # Set up system disk
    myinstances.setSystemDisk()
    # Set up a data disk
    dataDiskName = 'libing-test01-'
    dataDiskSize = 20
    dataDiskType = 'ssd'
    myinstances.setDataDisk(dataDiskName, dataDiskSize, dataDiskType)
    # Set up a second data disk
    dataDiskName = 'libing-test02-'
    dataDiskSize = 30
    dataDiskType = 'premium-hdd'
    myinstances.setDataDisk(dataDiskName, dataDiskSize, dataDiskType)
    # Set up elastic IP
    elasticIpBW = 1
    elasticIpprovider = 'bgp'
    myinstances.setElasticIp(elasticIpBW, elasticIpprovider)

    # Finally create instances
    resp = myinstances.createInstances()

    print resp
    # ['i-cp6gidfe23', 'i-h96pw8ngor']