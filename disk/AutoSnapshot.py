#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from jdcloud_sdk.core.credential import *
from jdcloud_sdk.services.disk.client.DiskClient import *
from jdcloud_sdk.services.disk.apis.CreateSnapshotRequest import *
from jdcloud_sdk.services.disk.models.SnapshotSpec import *
import logging
import datetime
import uuid
from apscheduler.schedulers.blocking import BlockingScheduler

'''
定时任务生成云硬盘快照，配置信息存放于AutoSnapshot.py 如下：

    [Credential]
    access_key=xxxxxxxxxxxxxxxx
    secret_key=xxxxxxxxxxxxxxxx
    
    [Disk-Id]
    # 云盘ID，多个ID以逗号分隔
    IDs=vol-xm0v4ww2fd,vol-pvzyktryhy
    
    [Region]
    RegionId=cn-north-1

'''

def snapshotJob():
    # 从AutoSnapshot.conf中获取信息
    cf = ConfigParser()
    cf.read('AutoSnapshot.conf')
    access_key = cf.get('Credential', 'access_key').strip()
    secret_key = cf.get('Credential', 'secret_key').strip()
    region_id = cf.get('Region', 'RegionId').strip()
    diskString = cf.get('Disk-Id', 'IDs')
    disks = [ id.strip() for id in diskString.split(',') ]

    # 将日志写入snapshot.log
    logging.basicConfig(filename='snapshot.log', filemode='a', level=logging.DEBUG, \
                        format='%(asctime)s - %(levelname)s - %(message)s')

    myCredential = Credential(access_key, secret_key)
    myClient = DiskClient(myCredential)

    # 依次为每个云硬盘制作快照
    for snapDisk in disks:
        logging.info('Creating snapshot for disk: ' + snapDisk)
        # 快照名为DiskID+日期，如：vol-xm0v4ww2fd-2018-07-26
        date = datetime.date.today()
        snapName = snapDisk + '-' + str(date)
        mySpec = SnapshotSpec(name=snapName, diskId=snapDisk)
        # 生成随机数用于幂等性校验参数
        clientToken = str(uuid.uuid4())[:5]
        try:
            myParam = CreateSnapshotParameters(regionId=region_id, snapshotSpec=mySpec, clientToken=clientToken)
            myRequest = CreateSnapshotRequest(parameters=myParam)
            resp = myClient.send(myRequest)
            if resp.error is not None:
                logging.error(resp.error.message)
            else:
                logging.info('Successfully created snapshot for disk: ' + snapDisk)
        except Exception, e:
            logging.error(e.message)

# 定时任务：每天凌晨3:30生成快照
scheduler = BlockingScheduler()
scheduler.add_job(snapshotJob, 'cron', hour=3, minute=30)
scheduler.start()