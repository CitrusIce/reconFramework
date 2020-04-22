import dns.resolver
import logging
from concurrent.futures import ThreadPoolExecutor

# if __name__ == "__main__":
#     import os, sys, inspect

#     currentdir = os.path.dirname(
#         os.path.abspath(inspect.getfile(inspect.currentframe()))
#     )
#     basedir = os.path.dirname(os.path.dirname(currentdir))
#     sys.path.insert(0, basedir)

from .base_class import Module
from .sql import SqlHelper


class CheckCDN(Module):
    """ task : string [host name]
    
    output : dict 
    
    e.g.

    { hostname : {"ip_address":ip, "use_CDN":True or False } """

    def __init__(self):
        super().__init__()
        self.data = dict()

    def exec(self):
        executor = ThreadPoolExecutor(max_workers=16)
        for host in self.task_list:
            executor.submit(self.check_cdn, host)
        executor.shutdown(wait=True)

    def get_output(self):
        return self.data

    def update_database(self, data):
        sql = SqlHelper()
        for host in data:
            sql.update(
                "project_assets", {"domain": host}, {"use_CDN": data[host]["use_CDN"]}
            )

    def empty(self):
        self.data = dict()

    def check_cdn(self, host):
        logging.info(self.__class__.__name__ + " check url: " + host)
        # 目标域名cdn检测
        myResolver = dns.resolver.Resolver()
        # myResolver.lifetime = myResolver.timeout = 2.0
        dnsserver = [
            ["223.6.6.6"],
            ["119.29.29.29"],
            ["182.254.116.116"],  # DNSPod
            ["180.76.76.76"],  # Baidu DNS
            ["223.5.5.5"],
            ["223.6.6.6"],  # AliDNS
            ["114.114.114.114"],
            ["114.114.115.115"],  # 114DNS
            # ["8.8.8.8"],
            # ["8.8.4.4"],  # Google DNS
            # ["1.0.0.1"],
            # ["1.1.1.1"],
            # ["208.67.222.222"],  # CloudFlare DNS
            # ["208.67.220.220"],  # OpenDNS
        ]
        result = []
        for i in dnsserver:
            myResolver.nameservers = i
            try:
                record = myResolver.query(host)
                result.append(record[0].address)
            except Exception as e:
                logging.warning(self.__class__.__name__ + " : " + str(e))
            if len(result) == 0:
                self.data[host] = {"use_CDN": True}
            elif len(result) == 1:
                self.data[host] = {"ip_address": result[0], "use_CDN": True}
            else:
                self.data[host] = {"ip_address": result[0], "use_CDN": False}


if __name__ == "__main__":
    test = CheckCDN()
    test.add_task("civdp.com")
    test.add_task("www.civdp.com")
    test.run()
    # print(check_cdn("baidu.com"))
