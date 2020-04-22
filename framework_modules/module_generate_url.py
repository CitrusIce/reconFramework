import requests
import sys
import os
import inspect
import logging
import urllib

from .base_class import Module
from .sql import SqlHelper


class MasmapUrlGenerator(Module):
    """ generate url from result of masmap
    
    input : dict result of module masmap
    
    output: list of urls"""

    def __init__(self):
        super().__init__()
        self.result = []

    def exec(self):
        for result_dict in self.task_list:
            for ip in result_dict:
                if "tcp" not in result_dict[ip]:
                    continue
                for port in result_dict[ip]["tcp"]:
                    if "http" in result_dict[ip]["tcp"][port]["name"]:
                        self.result.append(ip + ":" + str(port))
                    # if "http" == result_dict[ip]["tcp"][port]["name"]:
                    #     try:
                    #         requests.get("http://" + ip + ":" + str(port))
                    #         self.result.append("http://" + ip + ":" + str(port))
                    #     except:
                    #         self.result.append("https://" + ip + ":" + str(port))
                    # elif (
                    #     "ssl/http" == result_dict[ip]["tcp"][port]["name"]
                    #     or "https" == result_dict[ip]["tcp"][port]["name"]
                    # ):
                    #     self.result.append("https://" + ip + ":" + str(port))
                    # else:
                    #     continue

    def get_output(self):
        return self.result

    def update_database(self, data):
        pass

    def empty(self):
        self.result = []
