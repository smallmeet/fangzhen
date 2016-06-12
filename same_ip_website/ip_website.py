import re
import time
import requests

from fangzhen_db import FangZhenMysqlClient
from get_conf import GetConf


class IpWebsite:
	def __init__(self, conf):
		self.conf = conf
		self.base_url = 'http://s.tool.chinaz.com/same'
		self.mysql_client = FangZhenMysqlClient(conf)
		self.ip = str()
		self.headers = {
			'Referer': self.base_url,
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
		}

	def get_page_count(self, page=1):
		params = {
			's': self.ip,
			'page': str(page),
		}
		r = requests.get(self.base_url, headers=self.headers, params=params)
		try:
			page_count = int(re.findall(r'>共(\d+)页', r.text)[0])
		except:
			page_count = 1
		return page_count

	def get_website_list(self, page):
		params = {
			's': self.ip,
			'page': str(page),
		}
		r = requests.get(self.base_url, headers=self.headers, params=params)
		return list(set(re.findall(r'<a href=\'(.*?)\' target=_blank>', r.text)))

	def spider(self, ip_list):
		print('开始相同ip域名查询！')
		for ip in ip_list:
			self.ip = ip
			page_count = self.get_page_count()
			for page in range(1, page_count + 1):
				time.sleep(2)
				website_list = self.get_website_list(page)
				for website in website_list:
					self.mysql_client.insert_ip_website(args=(ip, website,))

		print('相同ip域名查询结束！')


def main():
	# ip_list = ['59.37.96.63', '120.27.34.24']
	conf = GetConf('../conf.xml')
	ip_list = ['59.37.96.63']
	ip_website = IpWebsite(conf)
	for ip in ip_list:
		print(ip)
		ip_website.spider(ip)


if __name__ == '__main__':
	main()
