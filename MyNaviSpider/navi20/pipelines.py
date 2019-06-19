# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings

class navi20Pipeline(object):
# 链接数据库
    client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
    # 数据库登录需要帐号密码的话
    # client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
    db = client[settings['MONGO_DB']]  # 获得数据库的句柄
    coll = db[settings['MONGO_COLL']]  # 获得collection的句柄

    def process_item(self, item, spider):
        postItem = dict(item)  # 把item转化成字典形式
        self.coll.insert(postItem)  # 向数据库插入一条记录
        #return item  # 会在控制台输出原item数据，可以选择不写