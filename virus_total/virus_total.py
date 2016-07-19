import requests
import os
import time

from get_conf import GetConf
from virus_total_db import VirusTotalMysqlClient


# 备案查询
class VirusTotal:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = VirusTotalMysqlClient(conf)
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

    def spider(self):
        print('开始 www.virustotal.com 爬取...')
        if not os.path.exists('log'):
            os.mkdir('log')
        md5 = ''
        while True:
            try:
                md5 = self.mysql_client.fetch_apk_black_list_info((1, ))[0][0]
                if not md5:
                    break
                print(md5)
                time.sleep(15)
                json_data = self.get_json_data(md5)
                if not json_data:
                    self.mysql_client.update_apk_black_list((md5, 1))
                    continue
                self.parse_data(md5, json_data['scans'])
                with open('log/result.txt', 'a') as f_result:
                    txt = md5 + ':完成查询!\n'
                    f_result.write(txt)
            except Exception as err:
                with open('log/err.txt', 'a') as f_err:
                    txt = md5 + ' ' + str(err) + '\n'
                    f_err.write(txt)
                self.mysql_client.update_apk_black_list((md5, 1))

        print('www.virustotal.com 爬取完成！')


def main():
    conf = GetConf('conf.xml')
    virus_total = VirusTotal(conf)
    virus_total.spider()


if __name__ == '__main__':
    main()
