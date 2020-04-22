import os
import subprocess
import urllib.parse
import sys
import os
import inspect
import logging
import json


from .base_class import Module
from .sql import SqlHelper

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basedir = os.path.dirname(currentdir)
# dirsearch_path = os.path.join(basedir, "tools", "dirsearch", "dirsearch.py")
brutespray_path = "/usr/share/brutespray/brutespray.py"
outputdir = os.path.join(basedir, "output", "brutespray")
if not os.path.exists(outputdir):
    os.mkdir(outputdir)


class BruteSpray(Module):
    """wrap of dirsearch

    input: absolute file path

    output: none
    """

    def __init__(self):
        super().__init__()

    def exec(self):
        for filename in self.task_list:
            logging.info("BruteSpray Module start ")
            # cmd = "/usr/bin/python3 {brutespray_path} -f {target} -o {outputdir}".format(
            #     brutespray_path=brutespray_path, target=filename, outputdir=outputdir
            # )
            cmd = "/usr/bin/python3 {brutespray_path} -f {target} -u test -p test -o {outputdir}".format(
                brutespray_path=brutespray_path, target=filename, outputdir=outputdir
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
