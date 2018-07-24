from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.StopInstanceRequest import *
from jdcloud_sdk.core.credential import *

access_key = 'ak'
secret_key = 'sk'

myCredential = Credential(access_key, secret_key)
myClient = VmClient(myCredential)

myParam = StopInstanceParameters(regionId='cn-north-1',instanceId='i-hakcy8cl94')
myRequest = StopInstanceRequest(myParam)

resp = myClient.send(myRequest)

if resp.error is not None:
    print resp.error.code, resp.error.message