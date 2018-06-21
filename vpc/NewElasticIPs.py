#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.services.vpc.models.ElasticIpSpec import *
from jdcloud_sdk.services.charge.models.ChargeSpec import *
from jdcloud_sdk.services.vpc.apis.CreateElasticIpsRequest import *
from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vpc.client.VpcClient import VpcClient

class NewElasticIPs(object):
    '''
    Create 1 or more public IPs
    '''
    def __init__(self, access_key, secret_key, regionId, bandwidthMbps, provider, elasticIpAddress=None, maxCount=1, chargeSpec=None):

        self.regionId = regionId
        self.bandwidthMbps = bandwidthMbps
        # bgp or no_bgp
        self.provider = provider
        # 指定弹性ip地址进行创建，当申请创建多个弹性ip时，必须为空
        self.elasticIpAddress = elasticIpAddress
        # 购买弹性ip数量；取值范围：[1,100]
        self.maxCount = maxCount
        self.chargeSpec = chargeSpec

        self.credential = Credential(access_key, secret_key)
        self.client = VpcClient(self.credential)
        print 'Client created...'

    def setChargeSpec(self, chargeMode=None, chargeUnit=None, chargeDuration=None):
        # chargeMode:  prepaid_by_duration:预付费，postpaid_by_usage:按用量后付费，postpaid_by_duration:按配置后付费，默认为postpaid_by_duration
        self.chargeSpec = ChargeSpec(chargeMode, chargeUnit, chargeDuration)
        print 'ChargeSpec created...'
        print 'ChargeMode: ' + self.chargeSpec.chargeMode

    def createElasticIps(self):
        if self.maxCount >1 and self.elasticIpAddress is not None:
            print 'If you want to create more than 1 elastic IP, please make elasticIpAddress is None!'
            return 1
        elasticIpSpec = ElasticIpSpec(bandwidthMbps=self.bandwidthMbps, provider=self.provider, chargeSpec=self.chargeSpec)
        elasticIpParam = CreateElasticIpsParameters(self.regionId, self.maxCount, elasticIpSpec)
        if self.elasticIpAddress is not None:
            elasticIpParam.setElasticIpAddress(self.elasticIpAddress)
        newRequest = CreateElasticIpsRequest(elasticIpParam)
        resp = self.client.send(newRequest)

        if resp.error is not None:
            print resp.error.code, resp.error.message

        my_resp = []
        # from unicode to utf8
        for i in resp.result['elasticIpIds']:
            my_resp.append(i.encode("utf-8"))

        return my_resp


if __name__ == '__main__':
    access_key = 'ak'
    secret_key = 'sk'
    regionId = 'cn-north-1'
    bandwidthMbps = 2
    provider = 'bgp'
    maxCount = 2

    myElasticIPs = NewElasticIPs(access_key, secret_key, regionId, bandwidthMbps, provider, maxCount=maxCount)

    myChargeMode = 'postpaid_by_usage'
    myElasticIPs.setChargeSpec(myChargeMode)

    myResp = myElasticIPs.createElasticIps()
    print myResp
    #['fip-akgdtfkslo', 'fip-kv5mwmsi74']