# -*- coding: utf-8 -*-

import requests
import os
import time
import re
import json

import postfile

from get_conf import GetConf
from virus_total_db import VirusTotalMysqlClient


# 备案查询
class VirusTotalUpload:
    def __init__(self):
        # self.conf = conf
        # self.mysql_client = VirusTotalMysqlClient(conf)
        self.base_url = 'https://www.virustotal.com/vtapi/v2/file/report'

        self.antivirus_list = {
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
            'Qihoo-360': '奇虎360',
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

    def parse_data(self, md5, scans_data):
        for (key, value, ) in scans_data.items():
            try:
                antivirus = self.antivirus_list[key]
            except:
                antivirus = key
            result = '没有发现病毒' if not value['result'] else value['result']
            indate = value['update']
            self.mysql_client.insert_virus_total((md5, antivirus, result, indate, ))

        self.mysql_client.update_apk_black_list((md5, 1, ))

    def get_json_data(self, md5):
        if self.mysql_client.select_virus_total((md5,)):
            with open('log/info.txt', 'a') as f_info:
                txt = md5 + ':记录已存在，跳过爬取!\n'
                f_info.write(txt)
                return None
        params = {
            "resource": "99017f6eebbac24f351415dd410d522d",
            "apikey": "83f339107d90ca7b812c99976990312f99f019be5cefbcef29f8493f44ae94dc",
        }
        json_data = requests.get(self.base_url, params=params).json()
        if 'Scan finished' not in json_data['verbose_msg']:
            with open('log/err.txt', 'a') as f_err:
                txt = md5 + ':apk尚无分析记录!\n'
                f_err.write(txt)
            return None

        return json_data

    def scan(self):
        requrl = "https://www.virustotal.com/vtapi/v2/file/report"
        r = requests.post(requrl, data={"apikey": apikey, "resource": md5})
        print(json.loads(r.text))
        print(json.loads(r.text)["positives"])
        time.sleep(15)

        scanurl = "https://www.virustotal.com/vtapi/v2/file/scan"
        r = requests.post(scanurl, data={"apikey": apikey}, files={"file": (name, open(name, "rb"))})
        print(json.loads(r.text))
        print(json.loads(r.text)["permalink"])
        time.sleep(15)

    def spider(self):
        print('开始 www.virustotal.com 爬取...')
        self.send()
        # self.upload()
        print('www.virustotal.com 爬取完成！')

    def upload(self):
        url1 = 'https://www.virustotal.com/en/file/upload/'
        time_prams = int(time.time() * 1000)
        params = {
            'sha256': 'b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57',
            '_': time_prams
        }
        headers1 = {
            'authority': 'www.virustotal.com',
            'method': 'GET',
            'path': '/en/file/upload/?sha256=b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57&_=' + str(time_prams),
            'scheme': 'https',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'referer': 'https://www.virustotal.com/en/',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'x-csrftoken': 'b236a73798cd68e5a779e97c9ca74d86',
            'x-requested-with': 'XMLHttpRequest',
        }
        r = requests.get(url1, headers=headers1, params=params)
        j = r.json()
        upload_url = j['upload_url'] + '&'
        print(upload_url)
        # if re.findall(r'&(.*?)=', upload_url)[0] == 'sha256':
        #     args = 'sha256=b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57/' + re.findall(r'(AMmf.*?)&', upload_url)[0]
        # else:
        #     args = str(time_prams) + '/' + re.findall(r'(AMmf.*?)&', upload_url)[0]
        args = str(time_prams) + '/' + re.findall(r'(AMmf.*?)&', upload_url)[0]
        # args = re.findall(r'_=(.*?)&', upload_url)[0]
        print(args)
        params = {
            'sha256': 'b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57',
            '_': args,
        }
        files = {
            'file': ('58dd447a48bd672fa963754cd1bdde34.ak', open(r'D:\apk\58dd447a48bd672fa963754cd1bdde34.apk', 'rb'), 'application/octet-stream'),
            # 'file': ('58dd447a48bd672fa963754cd1bdde34.apk', open(r'58dd447a48bd672fa963754cd1bdde34.apk', 'rb')),
            'remote_addr': (None, '125.69.66.103'),
            'ajax': (None, 'true'),
            'sha256': (None, 'b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57'),
            'last_modified': (None, '2016-07-15T06:10:28.858Z'),
        }

        file_size = os.path.getsize(r'D:\apk\58dd447a48bd672fa963754cd1bdde34.apk')
        path = '/_ah/upload/?sha256=b0ccc5a3474cd5b6705800454ddea47b4113b710760539fc3491ae11295ecd57&_=' + args
        headers = {
            'authority': 'www.virustotal.com',
            'method': 'POST',
            'path': path,
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'content-length': file_size + 745,
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryMEZIofVCtbxAMXVj',
            'origin': 'https://www.virustotal.com',
            'referer': 'https://www.virustotal.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        }
        url = 'https://www.virustotal.com/_ah/upload/'
        result = requests.post(url, headers=headers, files=files, params=params)
        print(result.url)
        print(result.text)
        with open('html.html', 'wb') as f:
            f.write(result.content)


def main():
    # conf = GetConf('conf.xml')
    virus_total_upload = VirusTotalUpload()
    virus_total_upload.spider()


if __name__ == '__main__':
    main()
