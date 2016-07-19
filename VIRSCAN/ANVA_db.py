from base_db import MysqlClient
from get_conf import GetConf


class ANVAMysqlClient:
	def __init__(self, conf):
		self.mysql_client = MysqlClient(conf)

	def insert_anva_msample_blacklist_info(self, args):
		self.mysql_client.insert('PRO_ANVA_MSAMPLE_BLACKLIST_INFO_INSERT', args)

	def insert_ANVA_apk_info(self, args):
		self.mysql_client.insert('PRO_ANVA_APK_INFO_INSERT', args)


if __name__ == '__main__':
	get_conf = GetConf('')
	mysql_client = ANVAMysqlClient(get_conf)
	# mysql_client.get_app_info()
	# mysql_client.insert_data()
