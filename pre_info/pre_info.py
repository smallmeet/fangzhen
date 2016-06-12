import re
import time
from urllib.parse import unquote

import chardet
import requests
import xlrd

from fangzhen_db import FangZhenMysqlClient
from get_conf import GetConf


# 备案查询
class PreInfo:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = FangZhenMysqlClient(conf)
        self.text = str()
        self.excel_file = 'temp.xls'

        self.base_url = 'http://whois.chinaz.com/reverse'
        self.headers = {
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def get_reverse_data(self, page_count, key, data_type, step):
        print('key:{key}'.format(key=key))
        first_list = set()
        second_list = set()
        url = 'http://whois.chinaz.com/pagehtml.ashx'
        for page in range(1, page_count + 1):
            time.sleep(5)
            params = {'type': data_type, 'page': str(page), 'host': key, }
            r = requests.get(url, headers=self.headers, params=params)
            try:
                res = re.findall(r'host=(.*?)&ddlSearchMode=', r.text)
                i = 0
                length = len(res)
                while i < length:
                    if res[i]:
                        first_list.add(res[i])
                    if res[i + step]:
                        second_list.add(res[i + step])
                    i += 3
            except:
                print('{key} 反向查询失败！'.format(key=key))
        return list(first_list), list(second_list)

    def reverse_by_domain(self, domain_list, scan_type=0):
        print('反向查询:根据域名反向查询')
        if domain_list == ['(', ')']:
            return
        for domain in domain_list:
            time.sleep(5)
            params = {'ddlSearchMode': '0', 'host': domain, }
            r = requests.get(self.base_url, headers=self.headers, params=params)
            try:
                res = re.findall(r'host=(.*?)&ddlSearchMode=', r.text)
                domain_attn = res[0].replace('+', ' ')
                if domain_attn:
                    domain_attn = (domain_attn if chardet.detect(domain_attn.encode('utf-8'))['encoding'] != 'ascii'
                                   else unquote(domain_attn, encoding='utf-8'))
                    print('注册者:{domain_attn}'.format(domain_attn=domain_attn))
                    if 'yinsi baohu' in domain_attn:
                        print('domain:{domain} 开启了隐私保护！'.format(domain=domain))
                    else:
                        self.mysql_client.insert_pre_domain_attn((domain_attn.strip(),))
                email = res[1]
                if email:
                    email = (email if chardet.detect(email.encode('utf-8'))['encoding'] != 'ascii'
                             else unquote(email, encoding='utf-8'))
                    if 'yinsibaohu' in email:
                        print('domain:{domain} 开启了隐私保护！'.format(domain=domain))
                    else:
                        self.mysql_client.insert_pre_email((email.strip(),))
            except:
                print('域名：{domain} 反向查询失败！'.format(domain=domain.strip()))
            self.mysql_client.insert_pre_domain((domain.strip(), ))
            self.mysql_client.insert_domain_info_domain((domain.strip(), ))
            self.mysql_client.update_pre_domain((domain.strip(), ))
            if scan_type == 1:
                self.mysql_client.update_ip_website_reverse((domain.strip(), ))
            print('域名:{domain}反向查询完成！'.format(domain=domain))

    def save_reverse_data_in_excel(self, key, mode):
        url = 'http://whois.chinaz.com/saveExc.ashx'
        form_data = {'_ddlSearchMode': mode, '_host': key, }
        r = requests.post(url, headers=self.headers, data=form_data)
        with open(self.excel_file, 'wb') as f:
            f.write(r.content)

    def get_reverse_data_by_excel(self, index1, index2):
        first_list = set()
        second_list = set()
        data = xlrd.open_workbook(self.excel_file)
        table = data.sheets()[0]
        row_count = table.nrows
        for i in range(2, row_count):
            first_list.add(table.row_values(i)[index1].strip())
            second_list.add(table.row_values(i)[index2].strip())

        return list(first_list), list(second_list)

    def reverse_by_email(self, email_list):
        if email_list == ['(', ')']:
            return
        for email in email_list:
            time.sleep(5)
            self.save_reverse_data_in_excel(email, mode='1')
            domain_list, attn_list = self.get_reverse_data_by_excel(index1=1, index2=2)
            for domain in domain_list:
                if domain:
                    domain = (domain if chardet.detect(domain.encode('utf-8'))['encoding'] != 'ascii'
                              else unquote(domain, encoding='utf-8'))
                    self.mysql_client.insert_pre_domain((domain,))
            for attn in attn_list:
                if attn:
                    attn = (attn if chardet.detect(attn.encode('utf-8'))['encoding'] != 'ascii'
                            else unquote(attn, encoding='utf-8'))
                    if ('yinsi baohu' in attn) or ('yinsibaohu' in attn):
                        print('email:{email} 开启了隐私保护！'.format(domain=email))
                    else:
                        self.mysql_client.insert_pre_domain_attn((attn,))
            self.mysql_client.update_pre_email((email,))

    def reverse_by_domain_attn(self, attn_list):
        if attn_list == ['(', ')']:
            return
        for attn in attn_list:
            time.sleep(5)
            self.save_reverse_data_in_excel(attn, mode='2')
            domain_list, email_list = self.get_reverse_data_by_excel(index1=1, index2=3)

            for domain in domain_list:
                if domain:
                    domain = (domain if chardet.detect(attn.encode('utf-8'))['encoding'] != 'ascii'
                              else unquote(domain, encoding='utf-8'))
                    self.mysql_client.insert_pre_domain((domain,))
            for email in email_list:
                if email:
                    email = (email if chardet.detect(attn.encode('utf-8'))['encoding'] != 'ascii'
                             else unquote(email, encoding='utf-8'))
                    if ('yinsi baohu' in email) or ('yinsibaohu' in email):
                        print('attn:{attn} 开启了隐私保护！'.format(attn=attn))
                    else:
                        self.mysql_client.insert_pre_email((email,))
            self.mysql_client.update_pre_domain_attn((attn,))

    def reverse(self):
        print('反向查询:循环收集数据中...')
        while True:
            try:
                domain_data = self.mysql_client.select_pre_domain()
                attn_data = self.mysql_client.select_pre_domain_attn()
                email_data = self.mysql_client.select_pre_email()
                if (domain_data == ()) and (attn_data == ()) and (email_data == ()):
                    break
                self.reverse_by_domain(domain_list=[x[0] for x in domain_data])
                self.reverse_by_email(email_list=[x[0] for x in email_data])
                self.reverse_by_domain_attn(attn_list=[x[0] for x in attn_data])
            except Exception as err:
                print(err)

    def spider(self):
        print('开始反向查询,收集数据中...')
        data = str(self.mysql_client.select_ip_website_reverse())
        if data != '()':
            url_list = re.findall(r'\'(http.*?)\'', data)
            self.reverse_by_domain(url_list, scan_type=1)
        self.reverse()
        print('done!')


def main():
    conf = GetConf('../conf.xml')
    pre_info = PreInfo(conf)
    pre_info.spider()


if __name__ == '__main__':
    main()
