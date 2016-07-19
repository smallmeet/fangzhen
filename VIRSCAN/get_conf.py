# -*- coding: utf-8 -*-
from xml.dom import minidom
import logging
import os


class GetConf:
    def __init__(self, conf_file):
        self.db_name = ''
        self.db_host = ''
        self.db_usr = ''
        self.db_passwd = ''
        self.db_port = ''

        self.log_file = ''
        self.habo_usr = ''
        self.habo_passwd = ''

        try:
            self.dom = minidom.parse(conf_file)
            self.root = self.dom.documentElement
        except Exception as err:
            logging.debug(err)
            str_err = os.getcwd() + '\\' + conf_file
            raise Exception('读取xml配置文件异常:', str_err)

        self.read_conf()

    def read_conf(self):
        try:
            self.db_host = self.root.getElementsByTagName('db_host')[0].childNodes[0].nodeValue
            self.db_name = self.root.getElementsByTagName('db_name')[0].childNodes[0].nodeValue
            self.db_usr = self.root.getElementsByTagName('db_usr')[0].childNodes[0].nodeValue
            self.db_passwd = self.root.getElementsByTagName('db_passwd')[0].childNodes[0].nodeValue
            self.db_port = self.root.getElementsByTagName('db_port')[0].childNodes[0].nodeValue
            self.log_file = self.root.getElementsByTagName('log_file')[0].childNodes[0].nodeValue
        except Exception as err:
            logging.debug(err)
            raise Exception('解析xml配置文件异常。')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='habo.log',
                        filemode='a')
    logging.debug('start apk analysis')

    conf_data = GetConf('hab1o_conf.xml')

    print(conf_data)
    print(conf_data.habo_usr)
