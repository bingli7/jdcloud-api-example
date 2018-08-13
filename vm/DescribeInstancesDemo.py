from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.DescribeInstancesRequest import *
import json

access_key = 'ak'
secret_key = 'sk'

regionId = 'cn-north-1'
instanceId = 'i-uvvtdzuxre'

myCredential = Credential(access_key, secret_key)
myClient = VmClient(myCredential)

myParam = DescribeInstanceParameters(regionId, instanceId)
myRequest = DescribeInstanceRequest(myParam)

resp = myClient.send(myRequest)
print json.dumps(resp.result, indent=2)