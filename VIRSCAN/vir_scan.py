import requests
import re
import time
import os
from lxml import etree

from get_conf import GetConf
from VIRSCAN.vir_scan_db import VirScanMysqlClient


# 备案查询
class VirScan:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = VirScanMysqlClient(conf)

        self.base_url = 'http://md5.virscan.org/'
        self.md5_url = str()
        self.report_url = str()
        self.url_list = list()
        self.source = str()
        self.md5 = str()
        self.md5_list = list()
        self.headers = {
            # 'Referer': self.base_url,
            # 'Host': 'http://md5.virscan.org/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
        self.antivirus_engine_list = {
            'antiy': '安天',
            'asquared': 'a-squared',
            'avast': 'AVAST!',
            'avg': 'AVG',
            'baidu': 'Baidu Antivirus',
            'baidusd': '百度杀毒',
            'bitdefender': 'Bitdefender',
            'clamav': 'ClamAV',
            'drweb': 'Dr.Web',
            'fortinet': 'Fortinet',
            'fprot': 'F-PROT',
            'fsecure': 'F-Secure',
            'gdata': 'GData',
            'ikarus': 'IKARUS',
            'jiangmin': '江民杀毒',
            'kaspersky': '卡巴斯基',
            'kingsoft': '金山毒霸',
            'mcafee': '迈克菲',
            'nod32': 'NOD32',
            'panda': '熊猫卫士',
            'pcc': '趋势科技',
            'qh360': '奇虎360',
            'qqphone': 'QQ手机',
            'quickheal': 'Quickheal',
            'rising': '瑞星',
            'sophos': 'SOPHOS',
            'symantec': '赛门铁克',
            'tachyon': 'nProtect',
            'thehacker': 'TheHacker',
            'tws': '费尔',
            'vba': 'Vba32',
            'virusbuster': 'VirusBuster',
        }

    def get_report_url(self, md5):
        self.md5 = md5
        self.md5_url = self.base_url + self.md5.lower() + r'.html'
        time.sleep(1)
        r = requests.get(self.md5_url, headers=self.headers)
        try:
            self.report_url = re.findall(r'"(http://r.virscan.org/report/.*?)"', r.text)[0]
        except IndexError:
            self.report_url = re.findall(r'"(http://r.virscan.org/.*?)"', r.text)[0]

    def get_report_data(self):
        time.sleep(1)
        r = requests.get(self.report_url, headers=self.headers)
        self.source = r.text
        self.url_list = list(set(re.findall(r'"(http://v.virscan.org/.*?)"', r.text)))

    def get_md5_list(self):
        url_list = [url.replace('.html', '/1.html') for url in self.url_list]
        md5_list = []
        for url in url_list:
            time.sleep(1)
            r = requests.get(url, headers=self.headers)
            count = int(re.findall(r'find(\d+)scan', r.text)[0])
            md5_list += re.findall(r'"http://md5.virscan.org/(.*?).html"', r.text)
            page = count // 20 + 1 if count % 20 == 0 else count // 20
            md5_list += self.get_md5(url, page)
        return md5_list

    def get_md5(self, url, page):
        md5_list = []
        url = url[:-6]
        urls = [url + str(i) + '.html' for i in range(2, page + 1)]
        for url in urls:
            time.sleep(1)
            r = requests.get(url, headers=self.headers)
            md5_list += re.findall(r'"http://md5.virscan.org/(.*?).html"', r.text)
        return md5_list

    def parse_data(self):
        selector = etree.HTML(self.source)
        sel_trs = selector.xpath('//*[@id="order_items"]/tbody/tr')
        time.sleep(1)
        for tr in sel_trs:
            time.sleep(1)
            try:
                antivirus = self.antivirus_engine_list[tr.xpath('td[1]/text()')[0]]
            except:
                antivirus = tr.xpath('td[1]/text()')[0]
            indate = tr.xpath('td[4]/text()')[0]
            try:
                result = tr.xpath('td[5]/a/font/text()')[0]
            except:
                result = tr.xpath('td[5]/font/text()')[0]
            result = '没有发现病毒' if result == 'Found nothing' else result
            self.mysql_client.insert_vir_scan((self.md5, antivirus, result, indate, ))
        self.mysql_client.update_apk_black_list((self.md5, 0))

    def spider(self):
        print('开始 md5.virscan.org 爬取...')
        if not os.path.exists('log'):
            os.mkdir('log')
        while True:
            time.sleep(1)
            md5 = self.mysql_client.fetch_apk_black_list_info((0, ))[0][0]
            if not md5:
                break
            print(md5)
            if self.mysql_client.select_vir_scan((md5,)):
                continue

            try:  # 如果没有记录 则查询下一个md5
                self.get_report_url(md5)
            except Exception as err:
                with open('log/err.txt', 'a') as f:
                    txt = self.md5 + '    ' + str(err) + '\n'
                    f.write(txt)
                self.mysql_client.update_apk_black_list((self.md5, 0))
                continue

            try:
                self.get_report_data()
                self.parse_data()
                md5_list = self.get_md5_list()
                for m in md5_list:
                    time.sleep(1)
                    if self.mysql_client.select_apk_black_list_info((m, ))[0][0] == 0:
                        self.mysql_client.insert_apk_black_list((m, 0, 0, 0))
                with open('log/info.txt', 'a') as f:
                    txt = self.md5 + '完成查询\n'
                    f.write(txt)
            except Exception as err:
                self.mysql_client.update_apk_black_list((self.md5, 0))
                with open('log/err.txt', 'a') as f:
                    txt = self.md5 + '    ' + str(err) + '\n'
                    f.write(txt)

        print('md5.virscan.org 爬取完成！')


def main():
    conf = GetConf('conf.xml')
    pre_info = VirScan(conf)
    pre_info.spider()


if __name__ == '__main__':
    main()
