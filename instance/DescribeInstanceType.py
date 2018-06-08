#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vm.client.VmClient import VmClient
from jdcloud_sdk.services.vm.apis.DescribeInstanceTypesRequest \
    import DescribeInstanceTypesParameters, DescribeInstanceTypesRequest


class DescribeInstanceType(object):
    """
    Get all the instances type for an specified region
    """
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def get_instances_type(self, region_id):
        credential = Credential(self.access_key, self.secret_key)
        client = VmClient(credential)
        try:
            parameters = DescribeInstanceTypesParameters(region_id)
            request = DescribeInstanceTypesRequest(parameters)
            resp = client.send(request)
            if resp.error is not None:
                print resp.error.code, resp.error.message
                return
            print resp.result
        except Exception, e:
            print e


if __name__ == '__main__':
    # access key and secret key for your JDCloud account
    access_key = 'xxxxxxxxxxxxxxxxxx'
    secret_key = 'xxxxxxxxxxxxxxxxxx'
    region_id = 'cn-north-1'

    my_instance = DescribeInstanceType(access_key, secret_key)

    my_instance.get_instances_type(region_id)
