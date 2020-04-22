
import sys
import json
import base64
import pickle

from framework_lib.base_class import Pipe, Controller
from framework_modules.oneforall import OneForAllWrap
from framework_modules.check_cdn import CheckCDN
from framework_modules.check_host_ssl import CheckHostSSL
from framework_modules.dirsearch import Dirsearch
from framework_modules.nmap_module import Nmap
from framework_modules.generate_url import MasmapUrlGenerator
from framework_modules.eyewitness import EyeWitness
from framework_modules.whatweb import WhatWeb

with open('controller_state.json','r') as f:
    state = json.load(f)
    
for module in state:
    print(module)
    a = pickle.loads(base64.b64decode(state[module]))
    pass