#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.common.models.Filter import *
from jdcloud_sdk.services.vm.client.VmClient import *
from jdcloud_sdk.services.vm.apis.DescribeInstanceTypesRequest import *
from jdcloud_sdk.services.vpc.models.NetworkInterfaceSpec import *
from jdcloud_sdk.services.vm.models.InstanceNetworkInterfaceAttachmentSpec import *
from jdcloud_sdk.services.vm.models.InstanceSpec import *
from jdcloud_sdk.services.vm.apis.CreateInstancesRequest import *
from jdcloud_sdk.services.vm.apis.DescribeInstancesRequest import *
from jdcloud_sdk.services.vpc.models.ElasticIpSpec import *
from jdcloud_sdk.services.vpc.apis.CreateElasticIpsRequest import *
from jdcloud_sdk.services.vpc.client.VpcClient import VpcClient
from jdcloud_sdk.services.vpc.apis.DescribeElasticIpsRequest import *
from jdcloud_sdk.services.vm.apis.AssociateElasticIpRequest import *
from jdcloud_sdk.services.disk.client.DiskClient import *
from jdcloud_sdk.services.disk.models.DiskSpec import *
from jdcloud_sdk.services.disk.apis.CreateDisksRequest import *
from jdcloud_sdk.services.vm.apis.AttachDiskRequest import *
from jdcloud_sdk.services.disk.apis.CreateSnapshotRequest import *
from jdcloud_sdk.services.disk.models.SnapshotSpec import *
from jdcloud_sdk.services.vm.apis.DescribeInstanceVncUrlRequest import *
import time
import sys
import uuid
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime

'''
创建IP资源池 -> 查询云主机库存 -> 批量创建云主机 -> 从资源池取IP -> 弹性IP绑定云主机 ->  挂载云硬盘 -> 开启定时任务快照备份
'''

# ak & sk
access_key = '<ak>'
secret_key = '<sk>'

# 日志输出
logger = logging.getLogger("PuGongYing")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
# 输出到文件pgy.log
file_handler = logging.FileHandler("pgy.log")
file_handler.setFormatter(formatter)
# 输出到console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class PgyDemo(object):

    def __init__(self, access_key, secret_key):
        # 用户账户ak, sk
        self.access_key = access_key
        self.secret_key = secret_key
        self.credential = Credential(access_key, secret_key)

    def create_eip(self, regionId, bandwidthMbps, provider, count):
        '''
        创建多个弹性IP
        :param regionId: 区域ID
        :param bandwidthMbps: 弹性IP带宽
        :param provider: bgp/no_bgp
        :param count: 弹性IP数量
        :return: 弹性IP列表
        '''
        try:
            eipSpec = ElasticIpSpec(bandwidthMbps=bandwidthMbps, provider=provider)
            eipParam = CreateElasticIpsParameters(regionId=regionId, maxCount=count, elasticIpSpec=eipSpec)
            eipRequest = CreateElasticIpsRequest(parameters=eipParam)
            eipClient = VpcClient(self.credential)
            resp = eipClient.send(eipRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            # 从返回结果获取弹性IP
            eipList = [ eip.encode('utf-8') for eip in resp.result['elasticIpIds'] ]
        except Exception, e:
            logger.exception(e)
            sys.exit('error!创建弹性IP失败！')
        return eipList

    def getIpFromEipId(self, regionId, eipList):
        '''
        从弹性IP的id获得IP地址
        :param regionId: 地域
        :param eipList: 弹性IP列表
        :return: IP地址列表
        '''
        try:
            # 过滤条件
            myFilter = Filter('elasticIpIds', eipList)
            myParam = DescribeElasticIpsParameters(regionId)
            myParam.setFilters([myFilter])
            myRequest = DescribeElasticIpsRequest(myParam)
            # 发送请求
            eipClient = VpcClient(self.credential)
            resp = eipClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            ipList = [ ip['elasticIpAddress'].encode('utf-8') for ip in resp.result['elasticIps'] ]
        except Exception, e:
            logger.exception(e)
            sys.exit('error！获取云主机状态失败！')
        return ipList

    def getEipIdFromIp(self, regionId, ipAddress):
        '''
        从公网IP地址获得弹性IP的id
        :param regionId: 区域
        :param ipAddress: 公网ip地址
        :return: 弹性IP的id
        '''
        try:
            ipList = [ ipAddress ]
            # 以IP地址作为过滤条件
            newFilter = Filter(name='elasticIpAddress', values=ipList)
            myParam = DescribeElasticIpsParameters(regionId)
            myParam.setFilters([newFilter])
            myRequest = DescribeElasticIpsRequest(myParam)
            myClient = VpcClient(self.credential)
            # 发送请求
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            eipId = resp.result['elasticIps'][0]['elasticIpId']
        except Exception, e:
            logger.exception(e)
            sys.exit('error！获取弹性IP的id失败！')
        return eipId

    def check_instanceTypes(self, regionId, az, instanceTypes=None):
        '''
        查看实例库存
        :param regionId: 地域
        :param az: 可用区
        :param instanceTypes: 实例规格列表
        :return: 库存dict
        '''
        # 过滤条件：指定规格类型列表+可用区
        myFilter = []
        filter_1 = Filter(name='instanceTypes', operator='eq', values=instanceTypes)
        myFilter.append(filter_1)
        filter_2 = Filter(name='az', operator='eq', values=az)
        myFilter.append(filter_2)
        try:
            # 指定参数
            myParam = DescribeInstanceTypesParameters(regionId)
            myParam.setFilters(myFilter)
            myRequest = DescribeInstanceTypesRequest(myParam)
            myClient = VmClient(self.credential)
            # 发送请求
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
        except Exception, e:
            logger.exception(e)
            sys.exit('error！获取云主机库存失败！')
        # 从返回结果获取库存信息
        instockDict = {}
        for instancetype in resp.result['instanceTypes']:
            instockDict[instancetype['instanceType'].encode('utf-8')] = instancetype['state'][0]['inStock']
        return instockDict

    def create_instances(self, regionId, az, instanceType, count, imageId, \
                         subnetId, name, password, description=None):
        '''
        创建云主机
        :param regionId: 地域
        :param az: 可用区
        :param instanceType: 实例规格
        :param count: 云主机数量
        :param imageId: 镜像ID
        :param subnetId: 子网ID
        :param name: 云主机name
        :param password: 云主机密码
        :param description: 云主机描述
        :return: 返回云主机ID列表
        '''
        try:
            # 网络配置
            networkinterfaceSpec = NetworkInterfaceSpec(subnetId=subnetId, az=az)
            networkSpec = InstanceNetworkInterfaceAttachmentSpec(networkInterface=networkinterfaceSpec)
            instanceSpec = InstanceSpec(az=az, instanceType=instanceType, imageId=imageId, \
                                        name=name, keyNames=None, primaryNetworkInterface=networkSpec, \
                                        systemDisk=None, dataDisks=None, password=password, \
                                        description=description)
            instanceParam = CreateInstancesParameters(regionId, instanceSpec)
            # 云主机数量
            instanceParam.setMaxCount(count)
            instanceRequest = CreateInstancesRequest(instanceParam)
            instanceClient = VmClient(self.credential)
            # 发送请求
            resp = instanceClient.send(instanceRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
        except Exception, e:
            logger.exception(e)
            sys.exit('error！创建云主机失败！')
        # 从返回结果得到instance id
        instanceId = [ id.encode('utf-8') for id in resp.result['instanceIds'] ]
        return instanceId

    def check_instance_status(self, regionId, instanceIds):
        '''
        获取云主机状态信息
        :param regionId: 区域
        :param instanceIds: 云主机列表
        :return: 云主机状态dict
        '''
        # 云主机ID作为过滤条件
        myFilter = [ Filter(name='instanceId', operator='eq', values=instanceIds) ]
        try:
            myParam = DescribeInstancesParameters(regionId)
            myParam.setFilters(myFilter)
            myRequest = DescribeInstancesRequest(myParam)
            myClient = VmClient(self.credential)
            # 发送请求
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            # 从返回结果获取云主机状态信息
            instanceStatus = {}
            for ins in resp.result['instances']:
                instanceStatus[ins['instanceId']] = ins['status']
        except Exception, e:
            logger.exception(e)
            sys.exit('error！获取云主机状态失败！')
        return instanceStatus

    def associate_eip(self, regionId, instanceId, eipId):
        '''
        绑定弹性IP至云主机
        :param regionId: 区域
        :param instanceId: 云主机ID
        :param eipId: 弹性IP id
        :return: 绑定成功的弹性IP id
        '''
        try:
            myParam = AssociateElasticIpParameters(regionId, instanceId, eipId)
            myRequest = AssociateElasticIpRequest(myParam)
            myClient = VmClient(self.credential)
            # 发送请求
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
        except Exception, e:
            logger.exception(e)
            sys.exit('error！绑定弹性IP失败！')
        return 0

    def create_disk(self, regionId, az, name, count, diskType, size, description):
        '''
        创建1个或多个云硬盘
        :param regionId: 区域
        :param az: 可用区
        :param name: 硬盘名
        :param count: 数量
        :param diskType: 高效云盘
        :param size: 大小（GB）
        :param description: 描述
        :return: 云盘ID列表
        '''
        try:
            # 幂等性校验token
            clientToken = str(uuid.uuid4())[:5]
            # Disk spec
            myDiskSpec = DiskSpec(az=az, name=name, diskType=diskType, diskSizeGB=size, description=description)
            myParam = CreateDisksParameters(regionId=regionId, diskSpec=myDiskSpec, maxCount=count, clientToken=clientToken)
            myRequest = CreateDisksRequest(myParam)
            myClient = DiskClient(self.credential)
            # 发送创建云盘请求
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            diskIds = [ id.encode('utf-8') for id in resp.result['diskIds'] ]
        except Exception, e:
            logger.exception(e)
            sys.exit('error！创建云盘失败！')
        return diskIds

    def attach_disk(self, regionId, instanceId, diskId):
        '''
        挂载云盘至云主机
        :param regionId: 区域
        :param instanceId: 云主机ID
        :param diskId: 云盘ID
        :return: 成功0
        '''
        try:
            myParam = AttachDiskParameters(regionId, instanceId, diskId)
            myRequest = AttachDiskRequest(parameters=myParam)
            myClient = VmClient(self.credential)
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
                sys.exit('error！挂载云盘失败！')
        except Exception, e:
            logger.exception(e)
            sys.exit('error！挂载云盘失败！')
        return 0

    def get_vnc(self, regionId, instanceId):

        try:
            myParam = DescribeInstanceVncUrlParameters(regionId, instanceId)
            myRequest = DescribeInstanceVncUrlRequest(myParam)
            myClient = VmClient(self.credential)
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
                sys.exit('获取云主机Vnc地址失败！')
            vncUrl = resp.result['vncUrl'].encode('utf-8')
        except Exception, e:
            logger.exception(e)
            sys.exit('error！获取云主机Vnc地址失败！')
        return vncUrl

# 定时快照任务
def cron_snapshot(regionId, diskList):
    '''
    备份任务，生成云硬盘快照
    :param regionId: 区域
    :param diskList: 云硬盘list
    :return:
    '''
    myCredential = Credential(access_key, secret_key)
    myClient = DiskClient(myCredential)
    for snapDisk in diskList:
        logger.info('Creating snapshot for disk: ' + snapDisk)
        # 快照名为DiskID+日期，如：vol-xm0v4ww2fd-2018-07-26
        date = datetime.date.today()
        snapName = snapDisk + '-' + str(date)
        mySpec = SnapshotSpec(name=snapName, diskId=snapDisk)
        # 生成随机数用于幂等性校验参数
        clientToken = str(uuid.uuid4())[:5]
        try:
            myParam = CreateSnapshotParameters(regionId=regionId, snapshotSpec=mySpec, clientToken=clientToken)
            myRequest = CreateSnapshotRequest(parameters=myParam)
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logger.error(resp.error.message)
            else:
                logger.info('Successfully created snapshot for disk: ' + snapDisk)
        except Exception, e:
            logger.error(e.message)
            sys.exit('error！备份' + snapDisk + '失败！')

###################################################################

#主流程
myDemo = PgyDemo(access_key, secret_key)

regionId = 'cn-north-1'

az = ['cn-north-1a']
instanceTypes = ['g.n2.medium', 'g.n2.large', 'g.n2.xlarge', 'g.n2.2xlarge']
# 获得库存信息，如：{'g.n2.xlarge': True, 'g.n2.large': True, 'g.n2.medium': True, 'g.n2.2xlarge': True}
inStock = myDemo.check_instanceTypes(regionId, az, instanceTypes)
logger.info('+' * 50)
logger.info('区域'+ regionId + '可用区' + str(az) + '云主机库存信息如下：')
for stockItem in inStock.items():
    if stockItem[1] == True:
        logger.info('恭喜！实例规格' + stockItem[0] + '有库存呢')
    else:
        logger.info('Sorry！实例规格' + stockItem[0] + '没有库存了~')

logger.info('+' * 50)
eipCount = 5
provider = 'bgp'
bandwidthMbps = 2
# 创建弹性IP资源池
logger.info('创建' + str(eipCount) + '个弹性IP.....')
eipList = myDemo.create_eip(regionId=regionId, bandwidthMbps=bandwidthMbps, provider=provider, count=eipCount)
logger.info('创建成功:')
logger.info(str(eipList))

logger.info('+' * 50)
logger.info('获取IP地址.....')
ipList = myDemo.getIpFromEipId(regionId, eipList)
logger.info('IP地址为：' + str(ipList))

logger.info('+' * 50)
# 开始创建云主机
instanceAz = 'cn-north-1a'
# 云主机规格
instanceType = 'g.n2.medium'
if inStock[instanceType] == False:
    sys.exit("该云主机规格没有库存了！")
# 创建2台云主机
vmCount = 2
# Tomcat私有镜像
imageId = '5de362a8-b5c7-4bc6-8b80-a7fab91475db'
# 云主机name
name = 'PuGongYing-Demo'
# 云主机密码
password = 'HelloWorld@618'
# 云主机描述
description = 'PuGongYing Demo'
# VPC和子网信息
vpcId = 'vpc-15pyju0awr'
subnetId = 'subnet-24dibywk2s'
instanceIds = myDemo.create_instances(regionId=regionId, az=az[0], instanceType=instanceType, \
                                      count=vmCount, imageId=imageId, subnetId=subnetId, \
                                      name=name, password=password, description=description)
logger.info('创建云主机成功！')
logger.info('云主机ID：' + str(instanceIds) )
logger.info('+' * 50)
logger.info('等待云主机运行......')
# 等待云主机都已正常运行
while True:
    instanceStatus = myDemo.check_instance_status(regionId, instanceIds)
    logger.info(instanceStatus)
    if instanceStatus.values() == [ u'running' for n in xrange(len(instanceStatus)) ]:
        logger.info('所有云主机都已正常运行')
        break
    else:
        time.sleep(10)
        continue

logger.info('+' * 50)
logger.info('为云主机绑定弹性IP...')
for instance in instanceIds:
    # 从IP资源池中取出一个公网IP
    eip = ipList.pop()
    eipId = myDemo.getEipIdFromIp(regionId, eip)
    resp = myDemo.associate_eip(regionId, instance, eipId)
    if resp == 0:
        logger.info('成功绑定IP' + eip + '至云主机' + instance)

logger.info('+' * 50)
diskAz = 'cn-north-1a'
name = 'PuGongYing-Disk'
# 创建云盘的数量
diskCount = 1
# 云盘类型：ssd/premium-hdd
diskType = 'ssd'
# 大小20GB
diskSize = 20
diskDescription = "SSD disk for PuGongYing"
logger.info('创建' + str(diskCount) + '块' + diskType + '云硬盘.....')
diskList = myDemo.create_disk(regionId, diskAz, name, diskCount, diskType, diskSize, diskDescription)
logger.info('云硬盘创建成功' + str(diskList))
time.sleep(20)

logger.info('+' * 50)
logger.info('挂载云硬盘' + diskList[0] + '至云主机' + instanceIds[0] + '.....')
myDemo.attach_disk(regionId, instanceIds[0], diskList[0])
logger.info('挂载云硬盘成功！')
time.sleep(20)

logger.info('+' * 50)
# 获取远程云主机Vnc地址
vncInstance = instanceIds[0]
logger.info('正在获取云主机' + vncInstance + '的远程登录Vnc地址.....')
vncUrl = myDemo.get_vnc(regionId, vncInstance)
logger.info('成功获取VNC地址: ' + vncUrl)

logger.info('+' * 50)
# 定时任务：每天凌晨3:30生成快照
hour = 3
minute = 30
scheduler = BlockingScheduler()
logger.info('定时快照任务运行中.....')
scheduler.add_job(cron_snapshot, 'cron', hour=hour, minute=minute, args=[regionId, diskList])
scheduler.start()