import requests
import csv

from ANVA_db import ANVAMysqlClient
from get_conf import GetConf


# 备案查询
class ANVA:
	def __init__(self, conf):
		self.res_file = 'temp.csv'
		self.conf = conf
		self.mysql_client = ANVAMysqlClient(conf)

		self.base_url = 'https://msample.anva.org.cn/stastic/blackList'
		self.headers = {
			'Referer': self.base_url,
			'Host': 'msample.anva.org.cn',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
		}

	def save_data_in_excel(self):
		url = 'https://msample.anva.org.cn/stastic/BlackSel.xlsx'
		form_data = {
			'time_start': '',
			'time_end': '',
			'condition': 'Android',
			'behavior': '',
			'md5': '',
			'page': '',
			'id': '',
		}
		r = requests.post(url, headers=self.headers, data=form_data)
		with open(self.res_file, 'wb') as f:
			f.write(r.content)

	def get_res_from_file(self):
		with open(self.res_file, 'r') as f:
			reader = csv.reader(f)
			index = 0
			for row in reader:
				if index == 0:
					index = 1
					continue
				apk_malicious_code_name = row[1].strip()
				apk_md5 = row[2].strip()
				apk_malicious_activity_type = row[3].strip()
				apk_os = row[4].strip()
				apk_data = (apk_md5, apk_malicious_code_name, apk_malicious_activity_type, apk_os, )
				self.mysql_client.insert_anva_msample_blacklist_info(args=apk_data)

	def spider(self):
		print('开始 msample.anva.org.cn 爬取...')
		self.save_data_in_excel()
		self.get_res_from_file()
		print('msample.anva.org.cn 爬取完成！')
		# page_count = self.get_page_count()
		# print(page_count)
		# for page in range(0, page_count):
		# 	try:
		# 		time.sleep(2)
		# 		offset = page * 20
		# 		self.get_apk_info(offset)
		# 	except:
		# 		continue


def main():
	conf = GetConf('conf.xml')
	pre_info = ANVA(conf)
	pre_info.spider()


if __name__ == '__main__':
	main()
