import sys
import logging

from framework_modules.base_class import Pipe, Controller
from framework_modules.module_oneforall import OneForAllWrap
from framework_modules.module_oneforall import OneForAllWrap
from framework_modules.module_check_cdn import CheckCDN
from framework_modules.module_check_host_ssl import CheckHostSSL
from framework_modules.module_dirsearch import Dirsearch
from framework_modules.module_nmap import Nmap
from framework_modules.module_generate_url import MasmapUrlGenerator
from framework_modules.module_eyewitness import EyeWitness
from framework_modules.module_whatweb import WhatWeb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
)

# controller
controller = Controller()
# module
oneforall = OneForAllWrap("test")
check_cdn = CheckCDN()
check_host_ssl = CheckHostSSL()
nmap = Nmap(max_workers=16)
nmap_url_generator = MasmapUrlGenerator()
dirsearch = Dirsearch()
eyewitness = EyeWitness()
whatweb = WhatWeb()


# add module to controller
# controller.push(check_cdn)
controller.push(check_host_ssl)
controller.push(oneforall)
controller.push(nmap)
controller.push(dirsearch)
controller.push(nmap_url_generator)
controller.push(eyewitness)
controller.push(whatweb)

# pipe
# oneforall -> check_cdn, check_host_ssl
# oneforall -> nmap


oneforall2nmap = Pipe(func=oneforall.get_ip, module=nmap)
oneforall2check_cdn = Pipe(func=oneforall.get_subdomain, module=[check_host_ssl])

oneforall.register_pipe(oneforall2check_cdn)
oneforall.register_pipe(oneforall2nmap)


# check cdn -> nmap
check_cdn2nmap = Pipe(
    func=lambda data: [
        data[hostname]["ip_address"]
        for hostname in data
        if not data[hostname]["use_CDN"]
    ],
    module=nmap,
)
check_cdn.register_pipe(check_cdn2nmap)

# nmap -> nmap_url_generator
nmap2nmap_url_generator = Pipe(module=nmap_url_generator)
nmap.register_pipe(nmap2nmap_url_generator)

# nmap_url_generator -> check_host_ssl
nmap_url_generator2check_host_ssl = Pipe(module=check_host_ssl)
nmap_url_generator.register_pipe(nmap_url_generator2check_host_ssl)

# check_host_ssl  -> dirsearch, eyewitness, whatweb
url2web_detect = Pipe(module=[whatweb, eyewitness, dirsearch])
# nmap_url_generator.register_pipe(url2web_detect)
check_host_ssl.register_pipe(url2web_detect)

# add task
oneforall.add_task("example.com")
# controller start
controller.run()
# controller.save_state()
