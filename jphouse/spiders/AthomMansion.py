#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Steven'

from scrapy.spiders import Spider
from scrapy.http.request import Request
from jphouse.items import MansionItem
from urllib.parse import urlencode
from datetime import datetime
import logging


class AthomeMansion(Spider):
    athome_headers = {"Content-Type": "application/x-www-form-urlencoded;",
                      "charset": "UTF-8",
                      "referer": "http://www.athome.co.jp"}
    name = "AthomeMansion"
    allowed_domains = ["www.athome.co.jp"]
    start_urls = ['http://www.athome.co.jp/mansion/ajax/list/propertylist/']
    # 房源类型
    crawl_types = ["shinchiku", "chuko"]
    # 情报公开日 JOHOKOKAI（全部=kj001、本日=kj002、3日内=kj003、1周内=kj004）
    JOHOKOKAI = "kj004"
    # 最多抓取的页数
    crawl_page_no = 100
    crawl_item_name = "ATHOME_MANSION"
    crawl_kens = ["osaka"]

    def start_requests(self):
        for url in self.start_urls:
            for crawlKen in self.crawl_kens:
                for crawlType in self.crawl_types:
                    for pageNo in range(self.crawl_page_no):
                        payload = {"SITE_TOP_URL": "http:\/\/www.athome.co.jp\/", "SITECD": "00000", "ITEM": "ks",
                                   "ART": "12",
                                   "MAIN_CODE": "mansion", "SUB_CODE": crawlType, "DOWN": "1", "KEN": crawlKen,
                                   "SORT": "33",
                                   "PAGENO": pageNo + 1, "ITEMNUM": "50", "JOHOKOKAI": self.JOHOKOKAI,
                                   "INDICATE": "SINGLE"}
                        yield Request(url, callback=self.get_mansion, method='POST', headers=self.athome_headers,
                                      body=urlencode(payload))

    def get_mansion(self, response):
        housenos = response.xpath("//*[@id='item-list']/div/@data-bukken-no").extract()
        # print(housenos)
        for houseno in housenos:
            self.houseLink = "http://www.athome.co.jp/mansion/" + houseno
            yield Request(self.houseLink, callback=self.get_mansion_content, method='GET', headers=self.athome_headers,
                          encoding='utf-8')

    def get_mansion_content(self, response):
        item = MansionItem()
        # 房屋名称
        house_name = response.xpath('//*[@id="item-detail_header"]/h1/span[2]/text()').extract()
        if len(house_name) > 0:
            item['house_name'] = house_name[0].strip()
        else:
            item['house_name'] = response.xpath(
                '//*[@id="contents_top"]/div[3]/div[2]/h1/text()').extract_first().strip()
        # 価格
        house_price = response.xpath(
            '//*[@id="item-detai_basic"]/div[@class="right"]/dl[1]/dd[1]/span/span/text()').extract()
        item['house_price'] = house_price[0].strip()
        # 階建 / 階
        house_floor = response.xpath(
            '//*[@id="item-detai_basic"]/div[@class="right"]/dl[1]/dd[1]/span/span/text()').extract()
        item['house_floor'] = house_floor[0].strip()
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
        house_address = response.xpath('//*[@id="item-detai_basic"]/div[2]/dl[3]/dd/text()').extract()
        if len(house_address) > 0:
            item['house_address'] = house_address[0].replace('（', '').replace('）', '').strip()
        # 築年月
        building_date = response.xpath('//*[@id="item-detai_basic"]/div[2]/dl[4]/dd[1]/text()').extract()
        if len(building_date) > 0:
            item['building_date'] = building_date[0].strip()
        # 専有面積
        house_area = response.xpath('//*[@id="item-detai_basic"]/div[2]/dl[4]/dd[2]/text()').extract()
        if len(house_area) > 0:
            item['house_area'] = house_area[0].strip()
        # 間取り
        house_layout = response.xpath('//*[@id="item-detai_basic"]/div[@class="right"]/dl[1]/dd[2]/text()').extract()
        if len(house_layout) > 0:
            item['house_layout'] = house_layout[0].strip()
        # 房屋类型
        house_type = response.xpath('//*[@id="item-detail_header"]/h1/span[1]/span/text()').extract()
        if len(house_type) > 0:
            item['house_type'] = house_type[0].strip()
        # 平米単価
        unit_price = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[1]/td[2]/text()').extract()
        if len(unit_price) > 0:
            item['unit_price'] = unit_price[0].strip()
        # 管理費等
        manage_fee = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[2]/td[1]/text()').extract()
        if len(manage_fee) > 0:
            item['manage_fee'] = manage_fee[0].strip()
        # 修繕積立金
        repair_fee = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[2]/td[2]/text()').extract()
        if len(repair_fee) > 0:
            item['repair_fee'] = repair_fee[0].strip()
        # 借地期間・地代（月額）
        land_rent = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[3]/td[1]/text()').extract()
        if len(land_rent) > 0:
            item['land_rent'] = land_rent[0].strip()
        # 権利金
        right_fee = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[3]/td[2]/text()').extract()
        if len(right_fee) > 0:
            item['right_fee'] = right_fee[0].strip()
        # 敷金 / 保証金
        guarantee_money = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[3]/td[2]/text()').extract()
        if len(guarantee_money) > 0:
            item['guarantee_money'] = guarantee_money[0].strip()
        # 維持費等
        maintain_fee = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[3]/td[2]/text()').extract()
        if len(maintain_fee) > 0:
            item['maintain_fee'] = maintain_fee[0].strip()
        # その他一時金
        other_fee = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[2]/tr[3]/td[2]/text()').extract()
        if len(other_fee) > 0:
            item['other_fee'] = other_fee[0].strip()
        # 建物名
        building_name = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[3]/tr[1]/td/text()').extract()
        if len(building_name) > 0:
            item['building_name'] = building_name[0].strip()
        # 設備
        house_equipments = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[3]/tr[2]/td/text()').extract()
        if len(house_equipments) > 0:
            item['house_equipments'] = house_equipments[0].strip()
        # 備考
        comments = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[3]/tr[3]/td/text()').extract()
        comment_str = ""
        for comment in comments:
            comment_s = comment.replace('（', '').replace('）', '').strip()
            if comment_s != "":
                comment_str += comment_s
                comment_str += ";"
        item['comments'] = comment_str
        # 間取り
        house_layout = response.xpath('//*[@id="item-detai_basic"]/div[2]/dl[4]/dd[3]/text()').extract()
        if len(house_layout) > 0:
            item['house_layout'] = house_layout[0].strip()
        # 専有面積
        house_area = response.xpath('//*[@id="item-detai_basic"]/div[2]/dl[4]/dd[2]/text()').extract()
        if len(house_area) > 0:
            item['house_area'] = house_area[0].strip()
        # バルコニー
        balcony_area = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]//tr[2]/td[2]/text()').extract()
        if len(balcony_area) > 0:
            item['balcony_area'] = balcony_area[0].strip()
        # 階建 / 階
        house_floor = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[3]/td[1]/text()').extract()
        if len(house_floor) > 0:
            item['house_floor'] = house_floor[0].strip()
        # 建物構造
        building_structure = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[3]/td[2]/text()').extract()
        if len(building_structure) > 0:
            item['building_structure'] = building_structure[0].strip()
        # 総戸数
        house_holds = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[4]/td[2]/text()').extract()
        if len(house_holds) > 0:
            item['house_holds'] = house_holds[0].strip()
        # リフォーム / リノベーション
        repairs = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[5]/td/text()').extract()
        if len(repairs) > 0:
            item['repairs'] = repairs[0].strip()
        # 駐車場
        parking = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[6]/td[1]/text()').extract()
        if len(parking) > 0:
            item['parking'] = parking[0].strip()
        # バイク置き場
        bike_parking = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[6]/td[2]/text()').extract()
        if len(bike_parking) > 0:
            item['bike_parking'] = bike_parking[0].strip()
        # 駐輪場
        motor_parking = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[7]/td[1]/text()').extract()
        if len(motor_parking) > 0:
            item['motor_parking'] = motor_parking[0].strip()
        # ペット
        pet_abled = response.xpath('//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[7]/td[2]/text()').extract()
        if len(pet_abled) > 0:
            item['pet_abled'] = pet_abled[0].strip()
        # 土地権利
        land_rights = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[8]/td[1]/text()').extract()
        if len(land_rights) > 0:
            item['land_rights'] = land_rights[0].strip()
        # 土地面積
        house_area = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[8]/td[2]/text()').extract()
        if len(house_area) > 0:
            item['house_area'] = house_area[0].strip()
        # 管理形態・方式
        manage_type = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[9]/td[1]/text()').extract()
        if len(manage_type) > 0:
            item['manage_type'] = manage_type[0].strip()
        # 国土法届出
        land_law_record = response.xpath(
            '//*[@id="item-detail_data"]/div/div[1]/table[4]/tr[9]/td[2]/text()').extract()
        if len(land_law_record) > 0:
            item['land_law_record'] = land_law_record[0].strip()

        # 房屋照片
        house_imgs = response.xpath(
            '//*[@id="detail-image_view"]/div[@class="left"]/div[@class="thumb-wrap"]//img/@src').extract()
        house_imgs_str = ""
        for house_img in house_imgs:
            house_imgs_str += house_img.split('?')[0].strip()
            house_imgs_str += ";"
            # saveImg.getAndSaveImg(house_img.split('?')[0], "D:\\360Downloads\\" + houseno)
        item['house_imgs'] = house_imgs_str

        # 条件等
        conditions = response.xpath(
            '//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[1]/td[1]/text()').extract()
        if len(conditions) > 0:
            item['conditions'] = conditions[0].strip()
        # 現況
        house_status = response.xpath(
            '//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[1]/td[2]/text()').extract()
        if len(house_status) > 0:
            item['house_status'] = house_status[0].strip()
        # 引渡し
        bargain = response.xpath('//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[2]/td[1]/text()').extract()
        if len(bargain) > 0:
            item['bargain'] = bargain[0].strip()

        # 物件番号
        house_no = response.xpath('//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[2]/td[2]/text()').extract()
        if len(house_no) > 0:
            item['house_no'] = house_no[0].strip()
        else:
            item['house_no'] = ""
            # 情報公開日
        info_open_time = response.xpath(
            '//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[3]/td[1]/text()').extract()
        if len(info_open_time) > 0:
            item['info_open_time'] = info_open_time[0].strip()
        # 次回更新予定日
        next_update_time = response.xpath(
            '//section[@id="item-detail_data"]/div[@class="clr"]/div[@class="left"]/table[5]//tr[3]/td[2]/text()').extract()
        if len(next_update_time) > 0:
            item['next_update_time'] = next_update_time[0].strip()
        item['scrawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S');
        item['house_link'] = self.houseLink
        item['_id'] = item['house_no']
        item['_item_name'] = self.crawl_item_name
        yield item
