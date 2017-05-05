#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Steven'

from twisted.enterprise import adbapi
import datetime
import pymysql.cursors
import logging
from jphouse.tools.MySQL import MySQL


class MysqlPipeline(object):
    default_collection_name = 'scrapy_items'

    def __init__(self, my_uri, my_port, my_db, my_user, my_pass):
        self.dbConn = MySQL(my_uri, my_user, my_pass, my_db, my_port)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            my_uri=crawler.settings.get('MYSQL_URI'),
            my_port=crawler.settings.get('MYSQL_PORT'),
            my_db=crawler.settings.get('MYSQL_DB'),
            my_user=crawler.settings.get('MYSQL_USER'),
            my_pass=crawler.settings.get('MYSQL_PASS')
        )

    def process_item(self, item, spider):
        self.dbConn.insert(item['_item_name'], item)
        self.dbConn.commit()
        return item

    def handle_error(self, e):
        logging.error(e)
