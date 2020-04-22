
import sys
import json
import base64
import pickle

from framework_modules.base_class import Pipe, Controller
from framework_modules.module_oneforall import OneForAllWrap
from framework_modules.module_check_cdn import CheckCDN
from framework_modules.module_check_host_ssl import CheckHostSSL
from framework_modules.module_dirsearch import Dirsearch
from framework_modules.module_nmap import Nmap
from framework_modules.module_generate_url import MasmapUrlGenerator
from framework_modules.module_eyewitness import EyeWitness
from framework_modules.module_whatweb import WhatWeb

with open('controller_state.json','r') as f:
    state = json.load(f)
    
for module in state:
    print(module)
    a = pickle.loads(base64.b64decode(state[module]))
    pass