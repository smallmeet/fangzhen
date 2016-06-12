from base_db import MysqlClient
from get_conf import GetConf


class CNERTMysqlClient:
    def __init__(self, conf):
        self.mysql_client = MysqlClient(conf)

    def insert_CNERT_apk_info(self, args):
        self.mysql_client.insert('PRO_CNERT_APK_INFO_INSERT', args)


if __name__ == '__main__':
    get_conf = GetConf('')
    mysql_client = CNERTMysqlClient(get_conf)
    # mysql_client.get_app_info()
    # mysql_client.insert_data()

