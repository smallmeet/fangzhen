from base_db import MysqlClient
from get_conf import GetConf


class FangZhenMysqlClient:
	def __init__(self, conf):
		self.mysql_client = MysqlClient(conf)

	# domain_info
	def insert_domain_info_domain(self, args):
		self.mysql_client.insert('PRO_DOMAIN_INFO_DOMAIN_INSERT', args)

	def select_domain_info(self):
		return self.mysql_client.select('PRO_DOMAIN_INFO_SELECT')

	def select_domain_info_icp(self):
		return self.mysql_client.select('PRO_DOMAIN_INFO_ICP_SELECT')

	def select_domain_info_whois(self):
		return self.mysql_client.select('PRO_DOMAIN_INFO_WHOIS_SELECT')

	def select_domain_info_web_scan(self):
		return self.mysql_client.select('PRO_DOMAIN_INFO_WEB_SCAN_SELECT')

	def update_domain_info(self, args):
		return self.mysql_client.update('PRO_DOMAIN_INFO_UPDATE', args)

	def update_domain_info_whois(self, args):
		return self.mysql_client.update('PRO_DOMAIN_INFO_WHOIS_UPDATE', args)

	def insert_domain_info_icp(self, args):
		self.mysql_client.insert('PRO_DOMAIN_INFO_ICP_INSERT', args)

	# pre_domain, pre_email, pre_attn
	def insert_pre_domain(self, args):
		self.mysql_client.insert('PRO_PRE_DOMAIN_INSERT', args)

	def insert_pre_domain_attn(self, args):
		self.mysql_client.insert('PRO_PRE_DOMAIN_ATTN_INSERT', args)

	def insert_pre_email(self, args):
		self.mysql_client.insert('PRO_PRE_EMAIL_INSERT', args)

	def select_pre_domain(self):
		return self.mysql_client.select('PRO_PRE_DOMAIN_SELECT')

	def select_pre_domain_attn(self):
		return self.mysql_client.select('PRO_PRE_DOMAIN_ATTN_SELECT')

	def select_pre_email(self):
		return self.mysql_client.select('PRO_PRE_EMAIL_SELECT')

	def update_pre_domain(self, args):
		return self.mysql_client.update('PRO_PRE_DOMAIN_UPDATE', args)

	def update_pre_domain_attn(self, args):
		return self.mysql_client.update('PRO_PRE_DOMAIN_ATTN_UPDATE', args)

	def update_pre_email(self, args):
		return self.mysql_client.update('PRO_PRE_EMAIL_UPDATE', args)

	# ip_website
	def select_ip_website_reverse(self):
		return self.mysql_client.select('PRO_IP_WEBSITE_REVERSE_SELECT')

	def update_ip_website_reverse(self, args):
		return self.mysql_client.update('PRO_IP_WEBSITE_REVERSE_UPDATE', args)

	# domain_webscan
	def insert_domain_webscan(self, args):
		self.mysql_client.insert('PRO_DOMAIN_WEBSCAN_INSERT', args)

	# ip_website
	def insert_ip_website(self, args):
		self.mysql_client.insert('PRO_IP_WEBSITE_INSERT', args)


if __name__ == '__main__':
	get_conf = GetConf('')
	mysql_client = FangZhenMysqlClient(get_conf)
