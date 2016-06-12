import re
import time
import requests
import logging
import socket
from lxml import etree

from get_conf import GetConf
from fangzhen_db import FangZhenMysqlClient


# 备案查询
class ICP:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = FangZhenMysqlClient(conf)

        self.url = 'http://icp.chinaz.com/'
        self.headers = {
            'Referer': self.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def get_guid(self):
        r = requests.get(self.url, headers=self.headers, timeout=20)
        guid = re.findall(r'value="(.*?)" name="guid"', r.text)[0]
        return guid

    def get_company_icp(self, page_source, icp_company, icp_property, domain):
        selector = etree.HTML(page_source)
        result_list = selector.xpath('//tbody[@id="result_table"]/tr')
        count = 0
        for result in result_list:
            count += 1
            (icp_license, icp_name, icp_homepages, icp_review_time) = result.xpath('td/text()')
            icp_homepages.strip()
            for icp_homepage in icp_homepages.split(' '):
                if icp_homepage in domain:
                        icp_homepage = domain
                args = (icp_homepage, icp_license, icp_company, icp_property, icp_name, icp_review_time)
                self.mysql_client.insert_domain_info_icp(args)

    def valid_ip(self, address):
        try:
            socket.inet_aton(address)
            return True
        except:
            return False

    def spider(self):
        print('开始域名ICP查询！')
        data = str(self.mysql_client.select_domain_info_icp())
        # res_list = re.findall(r'\'(http.*?)\'', data)
        res_list = re.findall(r'\'(.*?)\'', data)
        url_list = [url for url in res_list if not self.valid_ip(url)]
        print(url_list)
        for url in url_list:
            try:
                time.sleep(2)
                guid = self.get_guid()
                domain = url
                url = re.findall(r'(http://)?(www\.)?(.*)', url)[0][2]
                params = {
                    'hidesel': '网站域名',
                    's': url,
                    'guid': guid,
                    'code': '',
                    'havecode': '0',
                }
                r = requests.get(self.url, params=params, headers=self.headers, timeout=20)
                icp_company = re.findall(r'主办单位名称</span><p>(.*?)<', r.text)[0]
                icp_property = re.findall(r'主办单位性质</span><p>(.*?)<', r.text)[0]
                icp_license = re.findall(r'网站备案/许可证号</span><p>(.*?)<', r.text)[0]
                icp_name = re.findall(r'网站名称</span><p>(.*?)<', r.text)[0]
                icp_homepages = re.findall(r'网站首页网址</span><p class="Wzno">(.*?)<', r.text)[0]
                icp_review_time = re.findall(r'审核时间</span><p>(.*?)<', r.text)[0]

                for icp_homepage in icp_homepages.split(' '):
                    if icp_homepage in domain:
                        icp_homepage = domain
                    args = (icp_homepage, icp_license, icp_company, icp_property, icp_name, icp_review_time)
                    self.mysql_client.insert_domain_info_icp(args)
                self.get_company_icp(r.text, icp_company, icp_property, domain)
            except Exception as err:
                logging.error('url:{url}, {err}'.format(url=url, err=err))
                continue
        print('域名ICP查询结束！')


def main():
    conf = GetConf('conf.xml')
    icp = ICP(conf)
    icp.spider()


if __name__ == '__main__':
    main()
