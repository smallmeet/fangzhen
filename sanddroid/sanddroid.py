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
        self.json_data = []
        self.total = 1

        self.headers = {
            'Referer': 'http://sanddroid.xjtu.edu.cn/',
            'Host': 'sanddroid.xjtu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def parse_data(self):
        print(len(self.json_data['aaData']))
        time.sleep(15)
        for data in self.json_data['aaData']:
            indate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(data[0])))
            md5 = data[1]
            package_name = data[2]
            result = '没有发现病毒' if data[3] == 'UnDetected' else data[3]
            score = data[4]
            time.sleep(1)
            print(md5)
            if not self.mysql_client.select_sanddroid((md5, )):
                self.mysql_client.insert_sanddroid((md5, package_name, result, score, indate, ))
            if self.mysql_client.select_apk_black_list_info((md5, )):
                self.mysql_client.update_apk_black_list((md5, 2))
            else:
                self.mysql_client.insert_apk_black_list((md5, 0, 0, 1))

    def get_json_data(self):
        form_data = {
            'sEcho': '15',
            'iColumns': '5',
            'sColumns': '',
            'iDisplayStart': '0',
            'iDisplayLength': self.total,
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
            'is_search': 'false',
        }
        self.json_data = requests.post(self.url, headers=self.headers, data=form_data).json()
        self.total = self.json_data['iTotalDisplayRecords']

    def spider(self):
        print('开始 http://sanddroid.xjtu.edu.cn 爬取...')
        if not os.path.exists('log'):
            os.mkdir('log')
        try:
            self.total = 1
            self.get_json_data()
            print(self.total)
            self.get_json_data()
            print('get_json_data done')
            self.parse_data()
        except Exception as err:
            with open('log/err.txt', 'a') as f_err:
                txt = str(err) + '\n'
                f_err.write(txt)

        print('http://sanddroid.xjtu.edu.cn 爬取完成！')


def main():
    conf = GetConf('conf.xml')
    sanddroid = Sanddroid(conf)
    sanddroid.spider()


if __name__ == '__main__':
    main()
