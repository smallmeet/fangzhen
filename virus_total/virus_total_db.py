from base_db import MysqlClient
from get_conf import GetConf


class VirusTotalMysqlClient:
    def __init__(self, conf):
        self.mysql_client = MysqlClient(conf)

    def insert_virus_total(self, args):
        self.mysql_client.insert('PRO_VIRUS_TOTAL_INSERT', args)

    def update_apk_black_list(self, args):
        self.mysql_client.insert('PRO_APK_BLACK_LIST_UPDATE', args)

    def select_virus_total(self, args):
        return self.mysql_client.select('PRO_VIRUS_TOTAL_SELECT', args)

    def select_apk_black_list_info(self, args):
        return self.mysql_client.select('PRO_APK_BLACK_LIST_SELECT', args)

    def fetch_apk_black_list_info(self, args):
        return self.mysql_client.select('PRO_APK_BLACK_LIST_FETCH', args)


if __name__ == '__main__':
    get_conf = GetConf('')
    mysql_client = VirusTotalMysqlClient(get_conf)
# mysql_client.get_app_info()
# mysql_client.insert_data()
