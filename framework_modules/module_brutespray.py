import os
import subprocess
import urllib.parse
import sys
import os
import inspect
import json


from .base_class import Module
from .sql import SqlHelper

brutespray_path = "/usr/share/brutespray/brutespray.py"


class BruteSpray(Module):
    """wrap of dirsearch

    input: absolute file path

    output: none
    """

    def __init__(self):
        super().__init__()

    def exec(self):
        for filename in self.task_list:
            self.logger.info("BruteSpray Module start ")
            # cmd = "/usr/bin/python3 {brutespray_path} -f {target} -o {outputdir}".format(
            #     brutespray_path=brutespray_path, target=filename, outputdir=outputdir
            # )
            cmd = "/usr/bin/python3 {brutespray_path} -f {target} -u test -p test -o {outputdir}".format(
                brutespray_path=brutespray_path,
                target=filename,
                outputdir=self.outputdir,
            )
            proc = subprocess.Popen(cmd, shell=True,)
            proc.wait()

    def get_output(self):
        pass

    def update_database(self, data):
        pass

    def empty(self):
        for file_path in self.task_list:
            os.remove(file_path)


if __name__ == "__main__":
    pass
