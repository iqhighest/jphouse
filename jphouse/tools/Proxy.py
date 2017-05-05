# coding:utf-8
import requests
import json
import random

from jphouse import settings


class Proxy(object):
    def __init__(self):
        self.url = requests.get(settings.PROXY_URL).text

    def get_proxy(self):
        ip_ports = json.loads(self.url)
        ip = ip_ports[0]['ip']
        port = ip_ports[0]['port']
        proxy = 'http://%s:%s' % (ip, port)
        return proxy

    def get_proxies(self):
        ip_ports = json.loads(self.url)
        ip = random.choice(ip_ports)['ip']
        port = random.choice(ip_ports)['port']
        proxies = {
            'http': 'http://%s:%s' % (ip, port),
            'https': 'http://%s:%s' % (ip, port)
        }
        return proxies


if __name__ == "__main__":
    p = Proxy()
    # proxy = p.get_proxy()

    proxies = p.get_proxies()
    print("目前的代理服务器是：" + str(proxies))
    r = requests.get('http://ip.chinaz.com/getip.aspx', proxies=proxies)
    r.encoding = 'utf-8'
    print(r.text)
