import re
import time
import requests
import logging
import socket
from lxml import etree

from get_conf import GetConf
from fangzhen_db import FangZhenMysqlClient


# 备案查询
class WhoIs:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = FangZhenMysqlClient(conf)

        self.base_url = 'http://whois.chinaz.com/'
        self.headers = {
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def get_info(self, li):
        xpath_list = [
            'div[2]/text()',
            'div[2]/span[1]/text()',
            'div[2]/p[1]/a[1]/text()',
            'div[2]/div[1]/span[1]/text()'
        ]
        value = ''
        for xpath in xpath_list:
            try:
                temp_list = [x for x in li.xpath(xpath) if x.strip()]
                if temp_list:
                    value = ';'.join(temp_list)
                    break
            except:
                pass

        return value

    def default(self):
        key_map = {
            '域名': 'domain_name',
            '注册商': 'registrar',
            '联系人': 'contacts',
            '联系方式': 'contact_information',
            '更新时间': 'update',
            '创建时间': 'created',
            '过期时间': 'expiration',
            '域名服务器': 'domain_name_server',
            '公司': 'company',
            'DNS': 'DNS',
        }
        info = {
            'domain_name': 'N/A',
            'registrar': 'N/A',
            'contacts': 'N/A',
            'contact_information': 'N/A',
            'update': 'N/A',
            'created': 'N/A',
            'expiration': 'N/A',
            'domain_name_server': 'N/A',
            'company': 'N/A',
            'DNS': 'N/A',
        }

        return key_map, info

    def valid_ip(self, address):
        try:
            socket.inet_aton(address)
            return True
        except:
            return False

    def get_domain_name_info_list(self):
        data = str(self.mysql_client.select_domain_info_whois())
        res_list = re.findall(r'\'(.*?)\'', data)
        # res_list = re.findall(r'\'(http.*?)\'', data)
        return [url for url in res_list if not self.valid_ip(url)]

    def update_domain_info(self, domain, info):
        args = (
            domain,
            # info['domain_name'],
            info['registrar'],
            info['contacts'],
            info['contact_information'],
            info['update'],
            info['created'],
            info['expiration'],
            info['domain_name_server'],
            info['DNS'],
        )
        self.mysql_client.update_domain_info_whois(args)

    def spider(self):
        print('开始域名whois查询！')
        key_map, info = self.default()
        website_list = self.get_domain_name_info_list()
        print('共有：{lenght} url'.format(lenght=len(website_list)))
        for website in website_list:
            try:
                time.sleep(2)
                domain = website
                website = re.findall(r'(http://)?(www\.)?(.*)', website)[0][2]
                if not re.findall(r'[a-zA-Z]', website):
                    continue
                print(website)
                url = self.base_url + website
                r = requests.get(url, headers=self.headers, timeout=10)
                selector = etree.HTML(r.text)
                lis = selector.xpath('//ul[@id="sh_info"]/li')
                for li in lis:
                    if li.xpath('div[1]/@class')[0] == 'fl WhLeList-left':
                        key = key_map[li.xpath('div[1]/text()')[0]]
                    else:
                        key = key_map[li.xpath('div[1]/span/text()')[0]]

                    if key == 'company':
                        continue
                    info[key] = self.get_info(li)
                    if key == 'DNS':
                        break
                self.update_domain_info(domain, info)
            except Exception as err:
                # print(url)
                logging.error(err)
        print('域名whois查询结束！')


def main():
    conf = GetConf('conf.xml')
    who_is = WhoIs(conf)
    who_is.spider()


if __name__ == '__main__':
    main()
