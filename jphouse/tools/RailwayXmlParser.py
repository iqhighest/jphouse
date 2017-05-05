#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import etree
from decimal import Decimal
import MySQL
import logging
from jphouse.tools import GoogleMapAPI
import geohash


class RailwayXmlParser(object):
    def __init__(self, filePath):
        self.filePath = filePath
        self.ns = {"ksj": "http://nlftp.mlit.go.jp/ksj/schemas/ksj-app",
                   "gml": "http://www.opengis.net/gml/3.2",
                   "xlink": "http://www.w3.org/1999/xlink",
                   }
        self.railwayTypes = {
            "11": "普通鉄道JR",
            "12": "普通鉄道",
            "13": "鋼索鉄道",
            "14": "懸垂式鉄道",
            "15": "跨座式鉄道",
            "16": "案内軌条式鉄道",
            "17": "無軌条鉄道",
            "21": "軌道",
            "22": "懸垂式モノレール",
            "23": "跨座式モノレール",
            "24": "案内軌条式",
            "25": "浮上式",
        }
        self.providerTypes = {
            "1": "新幹線",
            "2": "JR在来線",
            "3": "公営鉄道",
            "4": "民営鉄道",
            "5": "第三セクター",
        }
        self.my = MySQL.MySQL('127.0.0.1', 'root', 'alibaba', 'gtjdb', 3306)

    def saveRailways(self):
        doc = etree.parse(self.filePath)
        railways = set()
        logging.debug("---------------------RailroadSection---------------------------")
        for node in doc.xpath("//ksj:RailroadSection", namespaces=self.ns):
            railwayName = node.xpath("ksj:railwayLineName", namespaces=self.ns)[0].text
            if railwayName not in railways:
                railways.add(railwayName)
                operationCompany = node.xpath("ksj:operationCompany", namespaces=self.ns)[0].text
                railwayType = self.railwayTypes.get(node.xpath("ksj:railwayType", namespaces=self.ns)[0].text)
                serviceProviderType = self.providerTypes.get(
                    node.xpath("ksj:serviceProviderType", namespaces=self.ns)[0].text)
                data = {'railway_name': railwayName, 'railway_type': railwayType, 'operation_company': operationCompany,
                        'service_provider_type': serviceProviderType}
                self.my.insert('gtj_railway', data)
                self.my.commit()
        logging.debug("=========================" + str(len(railways)) + "=========================")

    def saveStations(self):
        logging.debug("---------------------Station---------------------------")
        doc = etree.parse(self.filePath)
        for node in doc.xpath("//ksj:Station", namespaces=self.ns):
            stationName = node.xpath("ksj:stationName", namespaces=self.ns)[0].text
            railwayLineName = node.xpath("ksj:railwayLineName", namespaces=self.ns)[0].text
            count = self.my.query("select id from gtj_railway where railway_name='" + railwayLineName + "'")
            if count == 1:
                railway_id = self.my.fetchRow()[0]
            operationCompany = node.xpath("ksj:operationCompany", namespaces=self.ns)[0].text
            serviceProviderType = self.providerTypes.get(
                node.xpath("ksj:serviceProviderType", namespaces=self.ns)[0].text)
            railwayType = self.railwayTypes.get(node.xpath("ksj:railwayType", namespaces=self.ns)[0].text)
            # sectionID = node.xpath("ksj:railroadSection/@xlink:href", namespaces=self.ns)[0].replace("#", "")
            locationID = node.xpath("ksj:location/@xlink:href", namespaces=self.ns)[0].replace("#", "")
            locations = doc.xpath('//gml:Curve[@gml:id= $id]//gml:posList', id=locationID, namespaces=self.ns)[
                0].text
            locations = locations.strip().replace(" ", ",").replace('\n				', ';')
            lats = 0.00
            lngs = 0.00
            count = 0
            for location in locations.split(";"):
                lats = lats + float(location.split(",")[0])
                lngs = lngs + float(location.split(",")[1])
                count = count + 1
            if count != 0:
                lat = Decimal(lats / count).quantize(Decimal('0.000000000'))
                lng = Decimal(lngs / count).quantize(Decimal('0.000000000'))

            _geohash = geohash.encode(lat,lng,10)
            # gp = GoogleMapAPI()
            # data = gp.get_placeBylatlng(str(lat) + "," + str(lng))
            # town = data["town"]
            # city = data["city"]
            # province = data["province"]
            # address = data["address"]
            data = {'station_name': stationName, 'railway_id': railway_id,
                    'railway_name': railwayLineName, 'railway_type': railwayType,
                    'operation_company': operationCompany, 'service_provider_type': serviceProviderType,
                    'lat': lat, 'lng': lng, 'pos_list': locations,
                    # 'address': address, 'province': province, 'city': city, 'town': town,
                    "geohash": _geohash
                    }
            self.my.insert('gtj_railway_station', data)
            self.my.commit()
        logging.debug("==================================================")

    def updAddress(self):
        count = self.my.query("select id,lat,lng from gtj_railway_station where province =''")
        print(count)
        if count > 0:
            results = self.my.fetchAll()
            # print(results)
            for location in results:
                # print(location)
                id = location['id']
                print(id)
                lat = location['lat']
                lng = location['lng']
                gp = GoogleMapAPI.GoogleMapAPI()
                data = gp.get_placeBylatlng(str(lat) + "," + str(lng))
                if len(data) > 0:
                    self.my.update("gtj_railway_station", data, "id=" + id)
                    self.my.commit()

    def updGeohash(self):
        count = self.my.query("select id,lat,lng from gtj_railway_station ")
        print(count)
        if count > 0:
            results = self.my.fetchAll()
            print(results)
            for location in results:
                # print(location)
                id = location['id']
                lat = float(location['lat'])
                lng = float(location['lng'])
                _geohash = geohash.encode(lat, lng, 10)
                data = {
                    'geohash': _geohash
                }
                if len(data) > 0:
                    self.my.update("gtj_railway_station", data, "id=" + id)
                    self.my.commit()

    def selectByHash(self, lat, lng):
        # 精度为6基本控制在直线距离一公里以内，5基本在五公里以内
        _hash = geohash.encode(lat, lng, 6)
        count = self.my.query("select id,lat,lng,station_name  from gtj_railway_station where geohash like '" + _hash + "%'")
        print(count)
        if count > 0:
            results = self.my.fetchAll()
            # print(results)
            for location in results:
                _id = location['id']
                _lat = location['lat']
                _lng = location['lng']
                station_name = location['station_name']
                print(station_name)
                gp = GoogleMapAPI.GoogleMapAPI()
                print(_lat + "," + _lng)
                # print(gp.get_distance(str(lat) + "," + str(lng), _lat + "," + _lng))
                print(gp.calcDistanceFromAtoB(lat, lng, float(_lat), float(_lng)))
                print("-------------------------------")


if __name__ == "__main__":
    xp = RailwayXmlParser("N02-15.xml")
    xp.updAddress()
