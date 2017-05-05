#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Athome的一户建的抓取
__author__ = 'Steven'

from urllib.parse import urlencode
from datetime import datetime
import logging
from scrapy.spiders import Spider
from scrapy.http.request import Request
from jphouse.items import KodateItem
from jphouse.tools.Mongo import Mongo
from jphouse import settings


class AthomeKodate(Spider):
    athome_headers = {"Content-Type": "application/x-www-form-urlencoded;",
                      "charset": "UTF-8",
                      'User-Agent': settings.USER_AGENT,
                      "referer": "http://192.168.1.10:83"}
    name = "zhibo"
    allowed_domains = ["http://192.168.1.10:83"]
    start_urls = ['http://192.168.1.10:83/api/live/bidding/']

    def start_requests(self):
        payload = "app_platform=android&live_id=268&app_version=1.0&safecode=d8c4a4c6079cd0a01ac69cf45a77837d&bidding_amount=5&goods_id=97&member_name=18811352020&requestid="
        for url in self.start_urls:
            for i in range(1000):
                yield Request(url, callback=self.get_kodate, method='POST', headers=self.athome_headers,
                              body=payload + str(i))

    def get_kodate(self, response):
        i = 1
        # print("---------------------------------------------")
        # print(response)
        # print("---------------------------------------------")
