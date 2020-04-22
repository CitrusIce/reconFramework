import sys
import logging
import json
from ipaddress import ip_address

from framework_modules.module_nmap import Nmap, output_to_brutespray, brute_port_list
from framework_modules.module_brutespray import BruteSpray
from framework_modules.base_class import Pipe, Controller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("nmap_scan_brute_port_debug.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# nmap = Nmap(max_workers=32)
nmap = Nmap(port_list=brute_port_list, max_workers=32)
brutespray = BruteSpray()


# nmap.add_task("<ip>")

pipe = Pipe(func=output_to_brutespray, module=brutespray)
nmap.register_pipe(pipe)

controller = Controller()
controller.push(nmap)
controller.push(brutespray)
controller.run()
# with open("port_scan_result.json", "r") as f:
#     data = json.load(f)
# output_to_brutespray(data)
