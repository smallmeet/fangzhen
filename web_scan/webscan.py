import re
import time
import requests
import logging
import chardet

from get_conf import GetConf
from fangzhen_db import FangZhenMysqlClient


# 备案查询
class WebScan:
    def __init__(self, conf):
        self.conf = conf
        self.mysql_client = FangZhenMysqlClient(conf)
        self.text = str()

        self.base_url = 'http://tool.chinaz.com/webscan'
        self.headers = {
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }

    def get_domain_info_url_list(self):
        data = str(self.mysql_client.select_domain_info_web_scan())
        url_list = re.findall(r'\'(.*?)\'', data)

        return url_list

    def get_status_result(self):
        try:
            res = re.findall(r'"webstate":.*?,"msg":"(.*?)",', self.text)[0]
            status = (res if chardet.detect(res.encode('utf-8'))['encoding'] != 'ascii'
                      else res.encode('utf-8').decode('unicode-escape'))
        except:
            status = re.findall(r'id="jg_tips">(.*?)<', self.text)[0]
        return status

    def get_score_result(self):
        try:
            score = re.findall(r'"score":(\d+),"msg":', self.text)[0]
        except:
            score = re.findall(r'id="site_score">(.*?)<', self.text)[0]
        return score

    def get_vulnerability_result(self):
        desc_list = ['存在高危漏洞', '存在严重漏洞', '存在警告漏洞', '存在提示漏洞']
        vulnerability = '无漏洞'
        try:
            res_tuple = re.findall(r'"loudong":{"high":"(\d+)","mid":"(\d+)","low":"(\d+)","info":"(\d+)"',
                                   self.text)[0]
            for index, item in enumerate(res_tuple):
                if int(item) > 0:
                    vulnerability = desc_list[index]
                    break
        except:
            vulnerability = re.findall(r'id="loudong" class="fc_security">(.*?)<', self.text)[0]
        return vulnerability

    def get_key_result(self, key, regex):
        try:
            reg = '"' + key + '":{"level":(\d+),"msg":"(.*?)"}'
            res_tuple = re.findall(reg, self.text)[0]
            result = res_tuple[1] if int(res_tuple[0]) > 0 else '正常'
        except:
            result = re.findall(regex, self.text)[0]
        return result

    def spider(self):
        print('开始域名站点安全扫描！')
        index = 0
        website_list = self.get_domain_info_url_list()
        while index < len(website_list):
            try:
                domain = website_list[index]
                time.sleep(10)
                if not re.findall(r'[a-zA-Z]', domain):
                    print('domain: {domain} 不是有效的url地址'.format(domain=domain))
                    logging.warning('domain: {domain} 不是有效的url地址'.format(domain=domain))
                    index += 1
                    continue
                params = {
                    'host': domain,
                }
                print(domain)
                r = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
                time.sleep(1)
                if re.findall(r'验证码', r.text):
                    print('查询出现问题！')
                    time.sleep(100)
                    continue
                self.text = r.text
                status = self.get_status_result()
                score = self.get_score_result()
                vulnerability = self.get_vulnerability_result()
                fraudulent_websites = self.get_key_result('xujia',
                                                          r'id="diaoyu_sec" class="fc_security">(.*?)<')
                malicious_websites = self.get_key_result('guama',
                                                         r'id="trojan_sec" class="fc_security">(.*?)<')
                malicious_tampering = self.get_key_result('cuangai',
                                                          r'id="cuangai">(.*?)<')
                google_search_mask = self.get_key_result('google',
                                                         r'id="google_malware" class="fc_security">(.*?)<')

                args = (domain, status, score, vulnerability, fraudulent_websites,
                        malicious_websites, malicious_tampering, google_search_mask)

                print(args)
                self.mysql_client.insert_domain_webscan(args)
                index += 1
            except Exception as err:
                logging.error(err)
                raise err
        print('域名站点安全扫描结束！')


def main():
    conf = GetConf('conf.xml')
    web_scan = WebScan(conf)
    web_scan.spider()


if __name__ == '__main__':
    main()
