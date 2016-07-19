import requests
import os
import time

from get_conf import GetConf
from sanddroid_db import SanddroidMysqlClient


# 备案查询
class Sanddroid:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = SanddroidMysqlClient(conf)
        self.url = 'http://sanddroid.xjtu.edu.cn/apk_table_info'

        self.headers = {
            'Referer': 'http://sanddroid.xjtu.edu.cn/',
            'Host': 'sanddroid.xjtu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def parse_data(self, md5, json_data):
        indate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_data[0])))
        package_name = json_data[2]
        result = '没有发现病毒' if json_data[3] == 'UnDetected' else json_data[3]
        score = json_data[4]
        self.mysql_client.insert_sanddroid((md5, package_name, result, score, indate, ))

    def get_json_data(self, md5):
        if self.mysql_client.select_sanddroid((md5,)):
            with open('log/info.txt', 'a') as f_info:
                txt = md5 + ':记录已存在，跳过爬取!\n'
                f_info.write(txt)
                return None
        form_data = {
            'sEcho': '15',
            'iColumns': '5',
            'sColumns': '',
            'iDisplayStart': '0',
            'iDisplayLength': '50',
            'mDataProp_0': '0',
            'mDataProp_1': '1',
            'mDataProp_2': '2',
            'mDataProp_3': '3',
            'mDataProp_4': '4',
            'iSortCol_0': '1',
            'sSortDir_0': 'asc',
            'iSortingCols': '1',
            'bSortable_0': 'true',
            'bSortable_1': 'true',
            'bSortable_2': 'true',
            'bSortable_3': 'true',
            'bSortable_4': 'true',
            'is_search': 'true',
            'apk_md5': md5,
            'cert_sha1': '',
            'package': '',
            'malware_name': '',
        }
        json_data = requests.post(self.url, headers=self.headers, data=form_data).json()
        if not json_data['aaData']:
            with open('log/err.txt', 'a') as f_err:
                txt = md5 + ':apk尚无分析记录!\n'
                f_err.write(txt)
            return None

        return json_data

    def spider(self):
        print('开始 http://sanddroid.xjtu.edu.cn 爬取...')
        if not os.path.exists('log'):
            os.mkdir('log')
        md5 = ''
        while True:
            try:
                md5 = self.mysql_client.select_apk_black_list_info((2,))[0][0]
                if not md5:
                    break
                print(md5)
                time.sleep(2)
                json_data = self.get_json_data(md5)['aaData']
                if json_data:
                    self.parse_data(md5, json_data[0])
                    with open('log/result.txt', 'a') as f_result:
                        txt = md5 + ':完成查询!\n'
                        f_result.write(txt)
                self.mysql_client.update_apk_black_list((md5, 2,))
            except Exception as err:
                with open('log/err.txt', 'a') as f_err:
                    txt = md5 + ' ' + str(err) + '\n'
                    f_err.write(txt)
                self.mysql_client.update_apk_black_list((md5, 2))

        print('http://sanddroid.xjtu.edu.cn 爬取完成！')


def main():
    conf = GetConf('conf.xml')
    sanddroid = Sanddroid(conf)
    sanddroid.spider()


if __name__ == '__main__':
    main()
