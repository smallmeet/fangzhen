# -*- coding: utf-8 -*-
import pymysql
import logging
from get_conf import GetConf
# from get_conf import GetConf


class MysqlClient:
    def __init__(self, conf):
        self.mysql_cur = None
        self.mysql_conn = None
        self.related_id = -1
        self.apk_path = ''
        self.conf = conf

    def connect(self):
        try:
            self.mysql_conn = pymysql.connect(host=self.conf.db_host,
                                              port=int(self.conf.db_port),
                                              user=self.conf.db_usr,
                                              passwd=self.conf.db_passwd,
                                              db=self.conf.db_name,
                                              charset='utf8')
            self.mysql_conn.autocommit(True)
            self.mysql_cur = self.mysql_conn.cursor()

        except Exception as err:
            logging.error('数据库连接失败！')
            raise Exception(err)

    def close(self):
        self.mysql_cur.close()
        self.mysql_conn.close()

    def insert(self, proc, args):
        self.connect()
        try:
            self.mysql_cur.callproc(proc, args)

        except Exception as err:
            logging.error('存储过程{proc}调用失败, 参数:{args}'.format(proc=proc, args=args))
            raise Exception(err)
        finally:
            self.close()

    def select(self, proc, args=''):
        self.connect()
        try:
            if args:
                self.mysql_cur.callproc(proc, args)
            else:
                self.mysql_cur.callproc(proc)
            data = self.mysql_cur.fetchall()
            return data
        except Exception as err:
            logging.error('存储过程{proc}调用失败, 参数:{args}'.format(proc=proc, args=args))
            raise Exception(err)
        finally:
            self.close()

    def update(self, proc, args):
        self.connect()
        try:
            self.mysql_cur.callproc(proc, args)
        except Exception as err:
            logging.error('存储过程{proc}调用失败, 参数:{args}'.format(proc=proc, args=args))
            raise Exception(err)
        finally:
            self.close()

if __name__ == '__main__':
    get_conf = GetConf('')
    mysql_client = MysqlClient(get_conf)
    # mysql_client.get_app_info()
    mysql_client.insert_data()

