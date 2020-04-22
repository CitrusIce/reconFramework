import subprocess
import logging
import time
import sys
import os
import inspect

from .base_class import Module
from .sql import SqlHelper

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basedir = os.path.dirname(currentdir)


username = "reimu"
eyewitness_path = os.path.join(basedir, "tools", "EyeWitness","Python", "EyeWitness.py")
outputdir = os.path.join(basedir, "output", "EyeWitness")
if not os.path.exists(outputdir):
    os.mkdir(outputdir)
tmp_file_path = os.path.join(outputdir, "eyewitness_tmp.txt")


class EyeWitness(Module):
    """wrap of EyeWitness

    input : string url

    output : None"""

    def __init__(self):
        super().__init__()

    def exec(self):
        f = open(tmp_file_path, "w")
        for host in self.task_list:
            logging.info(self.__class__.__name__ + " add url to file: " + host)
            f.write(host + "\n")
        f.close()
        outdir_name = time.strftime("%Y-%m-%d-%H", time.localtime()) + "_reports"
        self.outdir_path = os.path.join(outputdir, outdir_name)
        logging.info(self.__class__.__name__ + " start capture")
        cmd = "sudo -u {username} /usr/bin/python3 {eyewitness_path} -f {tmp_file_path} -d {outdir_path} --no-prompt".format(
            username=username,
            eyewitness_path=eyewitness_path,
            tmp_file_path=tmp_file_path,
            outdir_path=self.outdir_path,
        )

        proc = subprocess.Popen(cmd, shell=True,)
        # proc = subprocess.Popen(cmd, stdout=open("/dev/null", "w"), shell=True,)
        proc.wait()

    def empty(self):
        # pass
        os.remove(tmp_file_path)

    def get_output(self):
        return None

    def update_database(self, data=None):
        sql = SqlHelper()
        screen_dir_path = os.path.join(self.outdir_path, "report.html")
        for url in self.task_list:
            # filename_without_ext = os.path.splitext(filename)[0]
            # filename_without_ext e.g. http.www.baidu.com
            # screenshot_path = os.path.join(screen_dir_path, filename)
            sql.update(
                "web_service", {"url": url}, {"screenshot_path": screen_dir_path}
            )


if __name__ == "__main__":
    eyewitness = EyeWitness()
    eyewitness.add_task("https://www.sogou.com")
    eyewitness.run()
