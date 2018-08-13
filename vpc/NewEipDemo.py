from jdcloud_sdk.core.credential import Credential
from jdcloud_sdk.services.vpc.client.VpcClient import VpcClient
from jdcloud_sdk.services.charge.models.ChargeSpec import *
from jdcloud_sdk.services.vpc.models.ElasticIpSpec import *
from jdcloud_sdk.services.vpc.apis.CreateElasticIpsRequest import *

access_key = 'ak'
secret_key = 'sk'
regionId = 'cn-north-1'
bandwidthMbps = 2
provider = 'bgp'
maxCount = 1

myCredential = Credential(access_key, secret_key)
myClient = VpcClient(myCredential)

myEipSpec = ElasticIpSpec(bandwidthMbps, provider)
myEipParam = CreateElasticIpsParameters(regionId, maxCount, myEipSpec)
myEipRequest = CreateElasticIpsRequest(myEipParam)

resp = myClient.send(myEipRequest)
