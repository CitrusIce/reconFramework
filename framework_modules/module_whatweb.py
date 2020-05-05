import subprocess
import time
import sys
import os
import inspect
import json


from .base_class import Module
from .sql import SqlHelper


class WhatWeb(Module):
    def __init__(self):
        super().__init__()
        self.tmp_file_path = os.path.join(self.outputdir, "tmp.txt")
        self.log_file_path = os.path.join(self.outputdir, "log.json")
        self.empty()

    def exec(self):
        f = open(self.tmp_file_path, "w")
        for url in self.task_list:
            self.logger.info(self.__class__.__name__ + " add url to file: " + url)
            f.write(url + "\n")
        f.close()
        cmd = 'whatweb -a 3 -U="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36" --log-json={logfile} -i {urlfile}'.format(
            logfile=self.log_file_path, urlfile=self.tmp_file_path,
        )

        self.logger.info(self.__class__.__name__ + " start detect")
        proc = subprocess.Popen(cmd, stdout=open(self.log_file_path, "a"), shell=True,)
        proc.wait()

    def get_output(self):
        f = open(self.log_file_path, "r", encoding="utf-8")
        result_list = json.load(f)
        f.close()
        return result_list

    def empty(self):
        try:
            os.remove(self.tmp_file_path)
            os.remove(self.log_file_path)
        except:
            pass

    def update_database(self, data=None):
        sql = SqlHelper()
        for target_dict in data:
            url = target_dict["target"]
            try:
                fingerprint = json.dumps(target_dict["plugins"])
                title = target_dict["plugins"]["Title"]["string"][0]
            except KeyError:
                title = ""
                self.logger.warning(url + " has no title ")
            finally:
                primary_key = {"url": url}
                insert_data = {"web_fingerprint": fingerprint, "title": title}
                sql.update("web_service", primary_key, insert_data)


if __name__ == "__main__":
    whatweb = WhatWeb()
    whatweb.add_task("http://www.baidu.com")
    whatweb.add_task("http://www.qq.com")

    whatweb.run()
    # whatweb.update_database()
