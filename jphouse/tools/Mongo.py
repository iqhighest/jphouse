#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Steven'

import pymongo
from scrapy.utils.project import get_project_settings


class Mongo(object):

    def __init__(self):
        settings = get_project_settings()
        self.mongo_uri = settings.get('MONGO_URI')
        self.mongo_db = settings.get('MONGO_DATABASE')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def selectByItem(self, item):
        return self.db[item['_item_name']].find_one(item['_id'])

    def selectByConditions(self, itemName, conditions):
        return self.db[itemName].find(conditions)

    def selectOneByConditions(self, itemName, conditions):
        return self.db[itemName].find_one(conditions)

    def countByConditions(self, itemName, dic):
        return self.db[itemName].count(dic)

    def saveItem(self, item):
        self.db[item['_item_name']].save(dict(item))
        return item

    def insertItem(self, item):
        self.db[item['_item_name']].insert(dict(item))
        return item
