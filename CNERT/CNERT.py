import requests
import time

from CNERT_db import CNERTMysqlClient
from get_conf import GetConf


# 备案查询
class CNERT:
	def __init__(self, conf):
		self.conf = conf
		self.mysql_client = CNERTMysqlClient(conf)

		self.base_url = 'https://appstore.anva.org.cn/Login/getMaliciousList'
		self.headers = {
			'Referer': 'https://appstore.anva.org.cn/Login/malicious',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
		}

	def get_page_count(self):
		params = {
			'limit': '20',
			'page': 1,
		}
		r = requests.get(self.base_url, params=params, headers=self.headers)
		json_data = r.json()
		return int(json_data['pageing']['end'])

	def get_apk_info(self, page):
		params = {
			'limit': '20',
			'page': page,
		}
		r = requests.get(self.base_url, params=params, headers=self.headers)
		print(r.url)
		json_data = r.json()
		for apk in json_data['list']:
			apk_url = apk['url']
			apk_md5 = apk['md5']
			apk_province = apk['province']
			apk_name = apk['app_name']
			apk_malicious_code_name = apk['cn_vname']
			apk_malicious_activity_type = apk['type']
			apk_state = apk['cn_state']
			market_name = apk['market_name']
			add_time = apk['add_time']

			apk_data = (apk_url, apk_md5, apk_province, apk_name, apk_malicious_code_name,
						apk_malicious_activity_type, apk_state, market_name, add_time,)
			self.mysql_client.insert_CNERT_apk_info(args=apk_data)

	def spider(self):
		page_count = self.get_page_count()
		for page in range(1, page_count+1):
			try:
				time.sleep(2)
				self.get_apk_info(page)
			except:
				continue


def main():
	conf = GetConf('conf.xml')
	pre_info = CNERT(conf)
	pre_info.spider()


if __name__ == '__main__':
	main()
