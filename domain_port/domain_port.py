import re
import time
import requests
import logging
from lxml import etree
import chardet
from urllib.parse import unquote
from get_conf import GetConf
# from pre_info_db import PreInfoMysqlClient


# 备案查询
class DomainPort:
    def __init__(self, conf):
        self.conf = conf
        # self.mysql_client = PreInfoMysqlClient(conf)
        self.text = str()

        self.base_url = 'http://tool.chinaz.com/port/'
        self.headers = {
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def get_key_result(self, regex):
        result = re.findall(regex, self.text)[0]
        return result

    def get_ports_status(self):
        params = {
            't': self.get_key_result(r'[?&]t=(.*?)[&\']'),
            'host': self.get_key_result(r'[?&]host=(.*?)[&\']'),
            'encode': self.get_key_result(r'[?&]encode=(.*?)[&\']'),
            'port': self.get_key_result(r'[?&]port=(.*?)[&\']'),
        }
        url = 'http://tool.chinaz.com/iframe.ashx'
        r = requests.get(url, headers=self.headers, params=params)

        selector = etree.HTML(r.text)
        port_sel = selector.xpath('//*[@id="contenthtml"]/p')


    def spider(self):
        print('开始端口扫描...')
        params = {
            'host': 'www.163.com',
            'ports': '80,8080,3128,8081,9080,1080,21,23,443,69,22,25,110,7001,9090,3389,1521,1158,2100,1433',
        }
        r = requests.get(self.base_url, headers=self.headers, params=params)
        self.text = re.findall(r'id="iframerequest"><iframe src=\'(.*?) ', r.text)[0]
        self.get_ports_status()
        print('done!')


def main():
    conf = GetConf('../conf.xml')
    domain_port = DomainPort(conf)
    domain_port.spider()


if __name__ == '__main__':
    main()
