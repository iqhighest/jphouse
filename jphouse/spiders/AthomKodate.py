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
                      "referer": "http://www.athome.co.jp"}
    name = "AthomeKodate"
    allowed_domains = ["www.athome.co.jp"]
    start_urls = ['http://www.athome.co.jp/kodate/ajax/list/propertylist/']
    # 房源类型 SHUMOKU（shinchiku=kb206/chuko=kb205、建築条件付き土地=kb203)
    SHUMOKU = ["kb206", "kb205"]
    # 情报公开日 JOHOKOKAI（全部=kj001、本日=kj002、3日内=kj003、1周内=kj004）
    JOHOKOKAI = "kj004"
    # 最多抓取的页数
    crawl_page_no = 100
    crawl_item_name = settings.ATHOME_KODATE_ITEM_NAME
    crawl_kens = ["osaka", "tokyo"]

    def start_requests(self):
        for url in self.start_urls:
            for crawlKen in self.crawl_kens:
                for crawlType in self.SHUMOKU:
                    for pageNo in range(self.crawl_page_no):
                        payload = {"SITE_TOP_URL": "http:\/\/www.athome.co.jp\/", "SITECD": "00000", "ITEM": "ks",
                                   "ART": "13", "MAIN_CODE": "kodate", "SHUMOKU": crawlType, "KEN": crawlKen,
                                   "DOWN": "1", "SORT": "33", "PAGENO": pageNo + 1, "ITEMNUM": "50",
                                   "JOHOKOKAI": self.JOHOKOKAI, "INDICATE": "SINGLE"}
                        # logging.debug("房源查询条件:" + str(payload))
                        yield Request(url, callback=self.get_kodate, method='POST', headers=self.athome_headers,
                                      body=urlencode(payload))

    def get_kodate(self, response):
        # print("---------------------------------------------")
        # print(response)
        # print("---------------------------------------------")
        housenos = response.xpath("//*[@id='item-list']/div/@data-bukken-no").extract()
        # nextPage = response.xpath("//ul[@class='paging typeInline right']/li[last()]/a[last()]/@page").extract()
        # if self.crawl_page_no == 1 and len(nextPage) > 0:
        #     self.crawl_page_no = int(nextPage[0])
        #     print("总页数：" + nextPage[0])
        for houseno in housenos:
            logging.debug("data-bukken-no:" + houseno)
            mongoDB = Mongo()
            item = mongoDB.selectOneByConditions(self.crawl_item_name, {"_id": houseno})
            if not item or datetime.strptime(item["next_update_time"], "%Y年%m月%d日") < datetime.today():
                self.houseLink = "http://www.athome.co.jp/kodate/" + houseno
                logging.debug("即将抓取房源：" + self.houseLink)
                yield Request(self.houseLink, callback=self.get_kodate_content, method='GET',
                              headers=self.athome_headers,
                              encoding='utf-8')

    def get_kodate_content(self, response):
        item = KodateItem()
        # 房屋名称
        house_name = response.xpath('//*[@id="item-detail_header"]/h1/span[@class="name"]/text()').extract()
        if len(house_name) > 0:
            item['house_name'] = house_name[0].strip()
        else:
            item['house_name'] = response.xpath(
                '//*[@id="contents_top"]/div[3]/div[2]/h1/text()').extract_first().strip()
        # 房屋类型
        house_type = response.xpath('//*[@id="item-detail_header"]/h1/span[@class="type"]/span/text()').extract()
        if len(house_type) > 0:
            item['house_type'] = house_type[0].strip()
        # 価格
        item['house_price'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[1]/dd[1]/span/span/text()').extract()[
                0].strip()
        # 間取り
        item['house_layout'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[1]/dd[2]/text()').extract()[0].strip()
        # 交通
        house_transports = response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[2]/dd/text()').extract()
        house_transport_str = ""
        for transport in house_transports:
            transport_str = transport.replace('（', '').replace('）', '').strip()
            if transport_str != "":
                house_transport_str += transport_str
                house_transport_str += ";"
        item['house_transports'] = house_transport_str
        # 所在地
        item['house_address'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[3]/dd/text()').extract()[0].replace(
                '（', '').replace('）', '').strip()
        # 築年月
        item['building_date'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[4]/dd[1]/text()').extract()[0].strip()
        # 建物面積
        item['house_area'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[4]/dd[2]/text()').extract()[0].strip()
        # 土地面積
        item['house_area'] = \
            response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[4]/dd[3]/text()').extract()[0].strip()
        # 房屋照片
        house_imgs = response.xpath(
            '//*[@id="detail-image_view"]/div[@class="left"]/div[@class="thumb-wrap"]//img/@src').extract()
        house_imgs_str = ""
        for house_img in house_imgs:
            house_imgs_str += house_img.split('?')[0].strip()
            house_imgs_str += ";"
            # saveImg.getAndSaveImg(house_img.split('?')[0], "D:\\360Downloads\\" + houseno)
        item['house_imgs'] = house_imgs_str
        # 価格
        item['house_price'] = response.xpath(
            '//*[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[2]//tr[1]/td[1]/text()').extract()[
            0].strip()
        # house_price = tree.xpath('//*[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]//th[text()="管理費等"]/following-sibling::td[1]/text()')[0]
        # 借地期間・地代（月額）
        item['land_rent'] = response.xpath(
            '//*[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[2]//tr[1]/td[2]/text()').extract()[
            0].strip()
        # 設備
        item['house_equipments'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[3]//tr[1]/td/text()').extract()[0].strip()
        # 備考
        comments = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[3]//tr[2]/td/text()').extract()
        comment_str = ""
        for comment in comments:
            comment_s = comment.replace('（', '').replace('）', '').strip()
            if comment_s != "":
                comment_str += comment_s
                comment_str += ";"
        item['comments'] = comment_str
        # 建物名
        item['building_name'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[1]/td[1]/text()').extract()[0].strip()
        # 間取り
        item['house_layout'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[2]/td[1]/text()').extract()[0].strip()
        # 建物面積
        item['house_area'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[2]/td[2]/text()').extract()[0].strip()
        # 土地面積
        item['land_area'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[3]/td[1]/text()').extract()[0].strip()
        # 私道負担面積
        item['road_area'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[3]/td[2]/text()').extract()[0].strip()
        # 築年月
        item['building_date'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[4]/td[1]/text()').extract()[0].strip()
        # 階建 / 階
        item['house_floor'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[4]/td[2]/text()').extract()[0].strip()
        # リフォーム / リノベーション
        item['repairs'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[5]/td[1]/text()').extract()[0].strip()
        # 駐車場
        item['parking'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[6]/td[1]/text()').extract()[0].strip()
        # 建物構造
        item['building_structure'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[6]/td[2]/text()').extract()[0].strip()
        # 土地権利
        item['land_rights'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[7]/td[1]/text()').extract()[0].strip()
        # 都市計画
        item['city_plan'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[7]/td[2]/text()').extract()[0].strip()
        # 用途地域
        item['land_purpose'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[8]/td[1]/text()').extract()[0].strip()
        # 接道状況
        item['road_status'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[8]/td[2]/text()').extract()[0].strip()
        # 建ぺい率
        item['building_density'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[9]/td[1]/text()').extract()[0].strip()
        # 容積率
        item['plot_ratio'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[9]/td[2]/text()').extract()[0].strip()
        # 地目
        item['land_purpose'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[10]/td[1]/text()').extract()[0].strip()
        # 地勢
        item['land_terrain'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[10]/td[2]/text()').extract()[0].strip()
        # 国土法届出
        item['land_law_record'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[11]/td[1]/text()').extract()[0].strip()
        # セットバック
        item['set_back'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[11]/td[2]/text()').extract()[0].strip()
        # 建築確認番号
        item['building_no'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[12]/td[1]/text()').extract()[0].strip()
        # 現況
        item['house_status'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[5]//tr[1]/td[1]/text()').extract()[0].strip()
        # 引渡し
        item['bargain'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[5]//tr[1]/td[2]/text()').extract()[0].strip()
        # 物件番号
        item['house_no'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[5]//tr[2]/td[1]/text()').extract()[0].strip()
        # 情報公開日
        item['info_open_time'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[5]//tr[3]/td[1]/text()').extract()[0].strip()
        # 次回更新予定日
        item['next_update_time'] = \
            response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[5]//tr[3]/td[2]/text()').extract()[0].strip()

        item['house_link'] = self.houseLink
        item['scrawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S');

        # 设置主键和表名，便于pipline处理
        item['_id'] = item['house_no']
        item['_item_name'] = self.crawl_item_name
        logging.debug("新抓取/更新房源:" + item['house_no'])
        yield item
