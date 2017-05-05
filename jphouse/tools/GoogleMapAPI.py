# coding:utf-8
import requests
import json
import logging
import geohash
from math import *

from jphouse import settings


class GoogleMapAPI(object):
    def get_distance(self, origin, destination, mode="walking"):
        '''
             起点和目的地提供行程距离和时间
             起点坐标：必须指定为“纬度,经度”形式。
             目的地坐标：必须指定为“纬度,经度”形式。
             出行模式：driving、walking、bicycling
             '''
        params = {
            "key": settings.GOOGLE_API_KEY,
            "mode": mode,
            "origins": origin,
            "destinations": destination,
        }
        duration = ""
        try:
            rsp = requests.get(settings.GOOGLE_MAP_DISTANCE_URL, params=params)
            logging.debug(rsp.text)
            distance = 0
            if rsp.status_code == 200:
                content = json.loads(rsp.text)
                if content["status"] == "OK":
                    duration = content["rows"][0]["elements"][0]["duration"]["text"]
                    distance = content["rows"][0]["elements"][0]["distance"]["text"]
                else:
                    logging.warning("GoogleAPI DISTANCE 调用失败：" + rsp.text)
            else:
                logging.warning("GoogleAPI DISTANCE 调用失败：" + rsp.text)
        except Exception as e:
            print(e)
            logging.error(e)
        return duration

    def get_direction(self, origin, destination, transit_mode="driving"):
        '''
                起点和目的地计算位置间路线
                起点坐标：必须指定为“纬度,经度”形式。
                目的地坐标：必须指定为“纬度,经度”形式。
                出行模式：driving、bus、subway、train、tram、rail
                '''
        params = {
            "key": settings.GOOGLE_API_KEY,
            "transit_mode": transit_mode,
            "origin": origin,
            "destination": destination,
        }
        duration = ""
        try:
            rsp = requests.get(settings.GOOGLE_MAP_DIRECTIONS_URL, params=params)
            logging.debug(rsp.text)
            distance = 0
            if rsp.status_code == 200:
                content = json.loads(rsp.text)
                if content["status"] == "OK":
                    duration = content["routes"][0]["legs"][0]["duration"]["text"]
                    distance = content["routes"][0]["legs"][0]["distance"]["text"]
                else:
                    logging.warning("GoogleAPI DIRECTION 调用失败：" + rsp.text)
            else:
                logging.warning("GoogleAPI DIRECTION 调用失败：" + rsp.text)
        except Exception as e:
            logging.error(e)
        return duration

    def get_nearby(self, location, types="shopping_mall|restaurant|store|train_station|bus_station", language="ja"):
        '''
             通过附近地点搜索
             location：检索地点信息所围绕的纬度/经度。必须指定为“纬度,经度”形式。
             radius ：定义返回地点结果的范围（以米为单位）。所允许的最大半径为 50000 米
             types ： 地点类型，常用的：airport、hospital、bank、bar、cafe、school、police、train_station、zoo、store、school
             shopping_mall、restaurant、university、bus_station
             '''
        params = {
            "key": settings.GOOGLE_API_KEY,
            "location": location,
            # "radius": radius,
            "types": types,
            "rankby": "distance",
            "language": language,
        }
        try:
            rsp = requests.get(settings.GOOGLE_MAP_NEARBYSEARCH_URL, params=params)
            logging.warning(rsp.text)
            if rsp.status_code == 200:
                content = json.loads(rsp.text)
                if content["status"] == "OK":
                    for place in content["results"]:
                        print(place["name"])
                        lat = float(location.split(",")[0])
                        lng = float(location.split(",")[1])
                        _lat = place["geometry"]["location"]["lat"]
                        _lng = place["geometry"]["location"]["lng"]
                        destination = str(_lat) + "," + str(_lng)
                        print(destination)
                        distance = self.calcDistanceFromAtoB(lat, lng, _lat, _lng)
                        print(distance)
                        print("---------------------------")
                else:
                    logging.warning("GoogleAPI NEARBY 调用失败：" + rsp.text)
            else:
                logging.warning("GoogleAPI NEARBY 调用失败：" + rsp.text)
        except Exception as e:
            logging.error(e)

    def get_placeBylatlng(self, location, language="ja"):
        '''
                根据坐标返回地理信息
                location：检索地点信息所围绕的纬度/经度。必须指定为“纬度,经度”形式。
                '''
        params = {
            "key": settings.GOOGLE_API_KEY,
            "latlng": location,
            "language": language,
            # "result_type": "country|political|locality",
        }
        result = {}
        try:
            rsp = requests.get(settings.GOOGLE_MAP_GEOCODE_URL, params=params)
            logging.warning(rsp.text)
            if rsp.status_code == 200:
                content = json.loads(rsp.text)
                # print(content)
                if content["status"] == "OK":
                    province = ""
                    city = ""
                    town = ""
                    address = ""
                    for address_com in content["results"]:
                        if 'sublocality_level_2' in address_com['types']:
                            address = address_com['formatted_address']
                            for addc in address_com['address_components']:
                                if 'administrative_area_level_1' in addc['types']:
                                    province = addc['short_name']
                                if 'locality' in addc['types'] and 'ward' not in addc['types']:
                                    city = addc['short_name']
                                if 'sublocality_level_1' in addc['types']:
                                    town = addc['short_name']
                            result = {"address": address, "town": town, "city": city, "province": province}
                            return result
                else:
                    logging.warning("GoogleAPI GEOCODE 调用失败：" + rsp.text)
            else:
                logging.warning("GoogleAPI GEOCODE 调用失败：" + rsp.text)
        except Exception as e:
            logging.error(e)
        return result

    def get_latlngByAddress(self, address, language="ja", region="jp"):
        '''
                根据坐标返回地理信息
                location：检索地点信息所围绕的纬度/经度。必须指定为“纬度,经度”形式。
                '''
        params = {
            "key": settings.GOOGLE_API_KEY,
            "address": address,
            "language": language,
            "region": region,
        }
        result = {}
        try:
            rsp = requests.get(settings.GOOGLE_MAP_GEOCODE_URL, params=params)
            logging.debug(rsp.text)
            if rsp.status_code == 200:
                content = json.loads(rsp.text)
                print(content)
                if content["status"] == "OK":
                    for address_com in content["results"]:
                        if len(address_com['address_components']) >= 5:
                            address = address_com['formatted_address']
                            address_component = address_com['address_components']
                            town = address_component[len(address_component) - 5]['short_name']
                            city = address_component[len(address_component) - 4]['short_name']
                            province = address_component[len(address_component) - 3]['short_name']
                            result = {"address": address, "town": town, "city": city, "province": province}
                            return result
                else:
                    logging.warning("GoogleAPI GEOCODE 调用失败：" + rsp.text)
            else:
                logging.warning("GoogleAPI GEOCODE 调用失败：" + rsp.text)
        except Exception as e:
            logging.error(e)
        return result

    def calcDistanceFromAtoB(this, Lat_A, Lng_A, Lat_B, Lng_B):
        """
        根据两点坐标，计算直线距离，单位为m
        :param Lat_A:
        :param Lng_A:
        :param Lat_B:
        :param Lng_B:
        :return:
        """
        ra = 6378.140  # 赤道半径 (m)
        rb = 6356.755  # 极半径 (m)
        distance = 0
        try:
            flatten = (ra - rb) / ra  # 地球扁率
            rad_lat_A = radians(Lat_A)
            rad_lng_A = radians(Lng_A)
            rad_lat_B = radians(Lat_B)
            rad_lng_B = radians(Lng_B)
            pA = atan(rb / ra * tan(rad_lat_A))
            pB = atan(rb / ra * tan(rad_lat_B))
            xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
            c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
            c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
            dr = flatten / 8 * (c1 - c2)
            distance = ra * (xx + dr)
        except Exception as e:
            distance = 0
        return distance

    def getcoordinateByDistance(self, location, distance):
        """
        :输入坐标和距离，返回坐标范围
        :param location:
        :param distance:
        :return:
        """
        # 各加0.007，或者lat+0.01，或者lng+0.011 =1km
        # 各加0.0139，或者lat+0.018，或者lng+0.0219 =2km
        # 各加0.0209，或者lat+0.027，或者lng+0.0329 =3km
        # 各加0.0348，或者lat+0.0451，或者lng+0.0546 =5km


if __name__ == "__main__":
    gp = GoogleMapAPI()
    location = "34.6870856,135.5265209"
    address = '大阪府大阪市北久宝寺町4-3-8-303室'
    # gp.get_placeBylatlng(location)
    gp.get_nearby(location, types="subway_station")
