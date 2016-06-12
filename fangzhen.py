import logging
import os
from logging.handlers import RotatingFileHandler

from get_conf import GetConf
from ICP.icp import ICP
from same_ip_website.ip_website import IpWebsite
from Whois.whois import WhoIs
from web_scan.webscan import WebScan
from pre_info.pre_info import PreInfo


class FangZhen:
    def __init__(self, conf):
        self.conf = conf

    def start(self):
        ip_list = ['59.37.96.63', '120.27.34.24', '125.69.66.103']
        # ip_list = ['120.27.34.24', '125.69.66.103']
        ip_website = IpWebsite(self.conf)
        ip_website.spider(ip_list)

        pre_info = PreInfo(self.conf)
        pre_info.spider()

        icp = ICP(self.conf)
        icp.spider()

        who_is = WhoIs(self.conf)
        who_is.spider()

        web_scan = WebScan(self.conf)
        web_scan.spider()


def set_log(log_file):
    if not os.path.isdir('log'):
        os.makedirs('log')
    formats = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    datefmts = '%a, %d %b %Y %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=formats, datefmt=datefmts)
    rotate_handler = RotatingFileHandler('log/' + log_file, maxBytes=10*1024*1024, backupCount=5)
    rotate_handler.setLevel(logging.INFO)
    rotate_handler.setFormatter(logging.Formatter(formats, datefmts))
    logging.getLogger('').addHandler(rotate_handler)


def main():
    conf = GetConf('conf.xml')
    set_log(conf.log_file)
    logging.info('fangzhen')
    fangzhen = FangZhen(conf)
    fangzhen.start()


if __name__ == '__main__':
    main()

