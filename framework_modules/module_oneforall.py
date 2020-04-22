import json
import os
import sys
import inspect
import subprocess
from ipaddress import ip_address
from ipaddress import ip_network

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# if __name__ == "__main__":

#     basedir = os.path.dirname(os.path.dirname(currentdir))
#     basedir = os.path.dirname(os.path.dirname(currentdir))
#     sys.path.insert(1, basedir)
# else:
#     sys.path.insert(0, currentdir)


from .base_class import Module
from .sql import SqlHelper

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basedir = os.path.dirname(currentdir)
# dirsearch_path = os.path.join(basedir, "tools", "dirsearch", "dirsearch.py")
outputdir = os.path.join(basedir, "output", "oneforall")
if not os.path.exists(outputdir):
    os.mkdir(outputdir)

oneforall_dir_path = os.path.join(basedir, "tools", "OneForAll", "oneforall")
oneforall_path = os.path.join(oneforall_dir_path, "oneforall.py")


class OneForAllWrap(Module):
    """a wrap of oneforall for subdomain discover 

task : string [host name]

output : list of dict

eg:
    [ {
    "id": 1,
    "type": "A",
    "valid": null,
    "new": 1,
    "url": "http://xx.com",
    "subdomain": "xx.com",
    "level": 1,
    "content": "xx.xx.xx.xx",
    "public": 1,
    "port": null,
    "status": null,
    "reason": null,
    "title": null,
    "banner": null
    }, ]
     """

    def __init__(self, project_name):
        super().__init__()
        self.project_name = project_name

    def empty(self):
        pass
        # self.host_list = []

    def exec(self):
        # self.host_list = self.task_list[:]
        # set the oneforall path into the first place of sys.path ortherwise it will raise an error
        # sys.path.insert(0, currentdir)
        for host in self.task_list:
            # cmd = "/usr/bin/python3.8 {oneforall_path} --target {target} --path {output} --req False --format json run"
            # cmd = cmd.format(
            #     oneforall_path=oneforall_path, target=host, output=outputdir
            # )
            cmd = "/usr/bin/python3.8 {oneforall_path} --target {target} --req False --format json run"
            cmd = cmd.format(oneforall_path=oneforall_path, target=host)

            proc = subprocess.Popen(cmd, shell=True,)
            # proc = subprocess.Popen(cmd, stdout=open("/dev/null", "w"), shell=True,)
            proc.wait()
            # proc = subprocess.Popen(
            #     cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            # )

    def get_output(self):
        result = list()
        for host in self.task_list:
            filename = os.path.join(
                oneforall_dir_path, "results", host + "_resolve_result.json"
            )
            with open(filename, "r") as f:
                tmp_list = json.loads(f.read())
            result += tmp_list
        return result

    def update_database(self, data):
        sql = SqlHelper()
        for dict_ in data:
            if dict_["content"] is None:
                continue
            elif "," in dict_["content"]:
                sql.update(
                    "project_assets",
                    {"domain": dict_["subdomain"]},
                    {
                        "ip_address": dict_["content"],
                        "project_name": self.project_name,
                        "use_CDN": True,
                    },
                )
            else:
                sql.update(
                    "project_assets",
                    {"domain": dict_["subdomain"]},
                    {
                        "ip_address": dict_["content"],
                        "project_name": self.project_name,
                        "use_CDN": False,
                    },
                )


def oneforall_get_ip(data):
    list_ = []
    for dict_ in data:
        # if len(list_) >= 100:
        #     break
        if dict_["content"] is None:
            continue
        if "," not in dict_["content"]:
            try:
                ip = ip_address(dict_["content"])
            except ValueError:
                logging.warning(dict_["content"] + " is not a valid ip!")
            else:
                if not ip.is_private:
                    list_.append(dict_["content"])
    return list_


def oneforall_get_class_c_ip(data):
    data = oneforall_get_ip(data)
    list_ = []
    for ip in data:
        ip_range = ip_network(ip + "/24", strict=False)
        list_.append(ip_range)
    list_ = list(set(list_))

    list_ = [str(ip) for network in list_ for ip in network]

    return list_


def oneforall_get_subdomain(data):
    list_ = []
    for dict_ in data:
        # if len(list_) >= 256:
        #     break
        if dict_["content"] is None:
            continue
        if "," not in dict_["content"]:
            try:
                ip = ip_address(dict_["content"])
            except ValueError:
                logging.warning(dict_["content"] + " is not a valid ip!")
            else:
                if not ip.is_private:
                    list_.append(dict_["subdomain"])
        else:
            list_.append(dict_["subdomain"])
    logging.info("Pipe list_ size: " + str(len(list_)))
    return list_


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
    )
    test = OneForAllWrap("test")
    test.add_task("civdp.com")
    test.run()
    # print(oneforall_get_class_c_ip(test.get_output()))
    # test.get_output()
    # print(check_cdn("baidu.com"))
