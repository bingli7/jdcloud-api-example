from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.DescribeImagesRequest import *

ak = '<ak>'
sk = '<sk>'

regionId = 'cn-north-1'

imageSource = 'private'

myCredential = Credential(ak, sk)
myClient = VmClient(myCredential)

myParam = DescribeImagesParameters(regionId)
myParam.setImageSource(imageSource)
myRequest = DescribeImagesRequest(myParam)

resp = myClient.send(myRequest)

print resp