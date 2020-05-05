import json
import os
import sys
import inspect
import time
import threading

import nmap
import re
from concurrent.futures import ThreadPoolExecutor

from .base_class import Module, Pipe
from .sql import SqlHelper


brute_port_list = "21,22,23,25,110,135,139,143,161,389,445,465,512,513,514,587,873,902,993,1023,1433,1521,3306,3690,5432,5631,5900,5984,6379,27017"
small_port_list = "21,22,23,25,53,80-89,110,135,139,143,161,389,443,445,465,873,993,995,1099,1433,1521,1723,2049,3128,3306,3389,3690,4100,5000,5432,5632,5900,5984,5985,6379,7001,8069,8443,8080-8090,9200,9300,9871,11211,27017,27018"
general_port_list = "1,7,9,13,19,21-23,25,37,42,49,53,69,79-81,85,105,109-111,113,123,135,137-139,143,161,179,222,264,384,389,402,407,443-446,465,500,502,512-515,523-524,540,548,554,587,617,623,689,705,771,783,873,888,902,910,912,921,993,995,998,1000,1024,1030,1035,1090,1098-1103,1128-1129,1158,1199,1211,1220,1234,1241,1300,1311,1352,1433-1435,1440,1494,1521,1530,1533,1581-1582,1604,1720,1723,1755,1811,1900,2000-2001,2049,2082,2083,2100,2103,2121,2199,2207,2222,2323,2362,2375,2380-2381,2525,2533,2598,2601,2604,2638,2809,2947,2967,3000,3037,3050,3057,3128,3200,3217,3273,3299,3306,3311,3312,3389,3460,3500,3628,3632,3690,3780,3790,3817,4000,4322,4433,4444-4445,4659,4679,4848,5000,5038,5040,5051,5060-5061,5093,5168,5247,5250,5351,5353,5355,5400,5405,5432-5433,5498,5520-5521,5554-5555,5560,5580,5601,5631-5632,5666,5800,5814,5900-5910,5920,5984-5986,6000,6050,6060,6070,6080,6082,6101,6106,6112,6262,6379,6405,6502-6504,6542,6660-6661,6667,6905,6988,7001,7021,7071,7080,7144,7181,7210,7443,7510,7579-7580,7700,7770,7777-7778,7787,7800-7801,7879,7902,8000-8001,8008,8014,8020,8023,8028,8030,8080-8082,8087,8090,8095,8161,8180,8205,8222,8300,8303,8333,8400,8443-8444,8503,8800,8812,8834,8880,8888-8890,8899,8901-8903,9000,9002,9060,9080-9081,9084,9090,9099-9100,9111,9152,9200,9390-9391,9443,9495,9809-9815,9855,9999-10001,10008,10050-10051,10080,10098,10162,10202-10203,10443,10616,10628,11000,11099,11211,11234,11333,12174,12203,12221,12345,12397,12401,13364,13500,13838,14330,15200,16102,17185,17200,18881,19300,19810,20010,20031,20034,20101,20111,20171,20222,22222,23472,23791,23943,25000,25025,26000,26122,27000,27017,27888,28222,28784,30000,30718,31001,31099,32764,32913,34205,34443,37718,38080,38292,40007,41025,41080,41523-41524,44334,44818,45230,46823-46824,47001-47002,48899,49152,50000-50004,50013,50500-50504,52302,55553,57772,62078,62514,65535"


def convert_ports_to_string(port_list):
    flag = False
    ports = ""
    for i in range(len(port_list)):
        if i == len(port_list) - 1:
            ports += str(port_list[i])
        elif i == 0:
            ports = str(port_list[0])
        elif port_list[i] + 1 == port_list[i + 1]:
            if flag:
                continue
            else:
                ports += "-"
                flag = True
        else:
            ports += str(port_list[i]) + ","
            flag = False
    return ports


class Nmap(Module):
    def __init__(self, port_list=None, max_workers=8):
        super().__init__()
        self.port_list = port_list
        self.max_workers = max_workers
        self.lock = threading.Lock()

    def exec(self):
        # return
        self.task_list = list(set(self.task_list))
        self.result = dict()
        executor = ThreadPoolExecutor(max_workers=self.max_workers)
        for ip in self.task_list:
            executor.submit(self.nmap_scan, ip)
        executor.shutdown(wait=True)

        self.output_file = os.path.join(
            self.outputdir,
            time.strftime("%Y-%m-%d-%H-%M", time.localtime())
            + "_port_scan_result.json",
        )
        with open(self.output_file, "w") as f:
            json.dump(self.result, f)

    def nmap_scan(self, ip):
        # print("start determine service/version of ports on host:", ip)
        # try:
        self.logger.info(self.__class__.__name__ + " scan target: " + ip)
        nm = nmap.PortScanner()
        if self.port_list != None:
            # ports = convert_ports_to_string(ports_list)
            ports = self.port_list
        else:
            ports = None
        arguments = "-T4 -sV -Pn -sS"
        nm.scan(
            hosts=ip, ports=ports, arguments=arguments, sudo=True,
        )
        #  if task.ip in nm:
        self.lock.acquire()
        self.result[ip] = nm[ip]
        self.lock.release()

    def get_output(self):
        # return self.result
        with open(self.output_file, "r") as f:
            result = json.load(f)
        return result

    def update_database(self, data):
        sql = SqlHelper()
        for ip in data:
            if "tcp" not in data[ip]:
                continue
            for port_id in data[ip]["tcp"]:
                service_data = {
                    "port_service": json.dumps(data[ip]["tcp"][port_id]),
                }
                primary_dict = {"ip_address": ip, "open_port_id": port_id}
                self.logger.debug(
                    self.__class__.__name__
                    + " "
                    + str(primary_dict)
                    + " "
                    + str(service_data)
                )
                sql.update("server_information", primary_dict, service_data)

    def output_to_brutespray(self, result_dict):
        data_list = []
        for ip in result_dict:
            if "tcp" not in result_dict[ip]:
                continue
            for port in result_dict[ip]["tcp"]:
                if result_dict[ip]["tcp"][port]["state"] == "closed":
                    continue
                dict_ = {
                    "host": ip,
                    "port": port,
                    "service": result_dict[ip]["tcp"][port]["name"],
                }
                data_list.append(json.dumps(dict_))
        filename = (
            time.strftime("%Y-%m-%d-%H-%M", time.localtime()) + "_brute_targets.json"
        )
        filename = os.path.join(self.outputdir, filename)
        f = open(filename, "w")
        for data in data_list:
            f.write(data + "\n")
        f.close()
        return filename


if __name__ == "__main__":

    _nmap = Nmap(port_list=small_port_list, max_workers=8,)
    tasklist = [
        "163.13.226.230",
        # "163.13.229.18",
        # "163.13.113.29",
        # "163.13.240.28",
        # "163.13.240.118",
        # "163.13.112.197",
        # "163.13.200.78",
        # "163.13.132.194",
    ]
    for ip in tasklist:
        _nmap.add_task(ip)
    _nmap.run()
    # masmap = Masmap()
    # masmap.add_task("127.0.0.1")
    # masmap.run()
