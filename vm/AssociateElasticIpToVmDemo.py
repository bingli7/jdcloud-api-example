#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.services.vm.apis.AssociateElasticIpRequest import *
from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.AssociateElasticIpRequest import *

class AssociateElasticIpToVmDemo(object):
    """
    Associate an elastic ip with an instance(Firstly need the instance ID and elastic ip ID
    """
    def __init__(self, access_key, secret_key, regionId, instanceId, elasticIpId):
        self.regionId = regionId
        # Instance ID: e.g. 'i-8hw0v3puvw'
        self.instanceId = instanceId
        # Elastic ip ID: e.g. 'fip-w97my7txc1'
        self.elasticIpId = elasticIpId

        self.credential = Credential(access_key, secret_key)
        self.client = VmClient(self.credential)
        print 'Client created...'

    def associateEIP(self):
        myParam = AssociateElasticIpParameters(self.regionId, self.instanceId, self.elasticIpId)
        myRequest = AssociateElasticIpRequest(myParam)
        resp = self.client.send(myRequest)

        if resp.error is not None:
            print resp.error.code, resp.error.message

        return resp

if __name__ == "__main__":
    access_key = 'ak'
    secret_key = 'sk'
    regionId = 'cn-north-1'
    instanceId = 'i-8hw0v3puvw'
    elasticIpId = 'fip-w97my7txc1'

    myDemo = AssociateElasticIpToVmDemo(access_key, secret_key, regionId, instanceId, elasticIpId)
    myDemo.associateEIP()
