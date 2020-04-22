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
dirsearch_path = os.path.join(basedir, "tools", "dirsearch", "dirsearch.py")
outputdir = os.path.join(basedir, "output", "dirsearch")
if not os.path.exists(outputdir):
    os.mkdir(outputdir)


# def dirsearch_api(url, path):
#     """
#     dirsearch_api(url [string],
#     outdir [string])

#     outdir -> relative path, if not exist it will be created
#     """
#     args = ["-u", url, "-e", "*", "--json-report", path]
#     Program(args=args)


class Dirsearch(Module):
    """wrap of dirsearch

    input: string  url

    output: dict
    """

    def __init__(self):
        super().__init__()
        self.result_files = []

    def exec(self):
        for url in self.task_list:
            logging.info("Dirsearch Module start at url: " + url)
            # outdir = os.path.join(currentdir, "reports")
            parsed = urllib.parse.urlparse(url)
            filename = (
                parsed.hostname
                + (("_" + str(parsed.port)) if parsed.port is not None else "")
                + ".json"
            )
            path = os.path.join(outputdir, filename)
            self.result_files.append(path)
            # dirsearch_api(url, path)
            cmd = "/usr/bin/python3 {dirsearch_path} -u {url} -e * --json-report={path}".format(
                dirsearch_path=dirsearch_path, url=url, path=path
            )
            proc = subprocess.Popen(cmd, stdout=open("/dev/null", "w"), shell=True,)
            # proc = subprocess.Popen(cmd, shell=True,)
            try:
                proc.wait(timeout=60 * 5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def get_output(self):
        result = dict()
        for file_path in self.result_files:
            if not os.path.exists(file_path):
                continue
            f = open(file_path, "r")
            try:
                tmp = json.load(f)
                result.update(tmp)
            except Exception as e:
                logging.error(self.__class__.__name__ + " " + str(e))

            f.close()
        return result

    def update_database(self, data):
        sql = SqlHelper()
        for url in data:
            for path_dict in data[url]:
                primary_dict = {"url": url, "available_path": path_dict["path"]}
                insert_data = {
                    "state_code": path_dict["status"],
                    "content_length": path_dict["content-length"],
                    "redirect": path_dict["redirect"],
                }
                sql.update("web_path_information", primary_dict, insert_data)

    def empty(self):
        for file_path in self.result_files:
            os.remove(file_path)
        self.result_files = []


if __name__ == "__main__":
    # import pickle
    # import base64

    # with open(os.path.join(basedir, "controller_state.json"), "r") as f:
    #     state = json.load(f)

    # a = pickle.loads(base64.b64decode(state["Dirsearch"]))

    # for module in state:
    #     print(module)
    #     a = pickle.loads(base64.b64decode(state[module]))
    #     pass
    dirsearch = Dirsearch()
    dirsearch.add_task("http://www.baidu.com")
    # dirsearch.add_task("http://220.181.38.150:80")
    # dirsearch.add_task("http://220.181.38.150:443")
    dirsearch.run()
    # outdir = os.path.join(currentdir, "reports") dirsearch_api("http://www.baidu.com", outdir)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("filename", help="file contain urls")
    # parser.add_argument("output", help="output dir name")
    # args = parser.parse_args()
    # with open(args.filename, "r") as f:
    #     for line in f:
    #         url = line.replace("\n", "").replace("\r", "")
    #         dirsearch_api(url, args.output)
