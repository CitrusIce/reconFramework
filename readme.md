# reconFramework

[中文文档](https://github.com/CitrusIce/reconFramework/blob/master/readme_zh.md)

There are many recon tools now, but no one can take care of every aspect of the reconnaissance, which is impossible, but we can assemble these tools and let them become a brand new tool to make our life easier, and that's why I write this.

The main idea of this framework is to wrap various tools (or you can write your own tool as a module) as modules and connect their input and output to automate the progress of information collecting, and the result data will be stored in a database.

## Installation

```bash
git clone https://github.com/CitrusIce/reconFramework.git
cd reconFramework
./install.sh

# after change database config in framework_config.py
python3 setup_database.py
```

## How to use 

I haven't finish this project yet and there has no interface for users and you have to changing the code in file reconFramework.py. Luckily I have done almost everthing for you and all you need is to change the domain name in the bottom of the file and run it. 

Here is what it will do

- collecting subdomains using oneforall
- scan some general ports and detect the service using nmap
- fingerprint scan using whatweb for web services
- directory scan using dirsearch
- capture web screenshot using EyeWitness

## requirements

- python >= 3.8

## module

This framework has preset some modules, here is the list.

- [dirsearch](https://github.com/maurosoria/dirsearch)
- [EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness)
- [Nmap](https://nmap.org/)
- [oneforall](https://github.com/shmilylty/OneForAll)
- [whatweb](https://github.com/urbanadventurer/WhatWeb)
- [BruteSpray](https://github.com/x90skysn3k/brutespray) (still working on it)
- check_cdn 
- check_host_ssl

Thanks to the developer of these greate tools! 

## Directory structure

```
.
├── clean_database.py       script to remove all data in database
├── framework_config.py     framework config file
├── framework_modules       all framework modules put in here
│   ├── base_class.py
│   ├── __init__.py
│   ├── module_brutespray.py
│   ├── module_check_cdn.py
│   ├── module_check_host_ssl.py
│   ├── module_dirsearch.py
│   ├── module_eyewitness.py
│   ├── module_generate_url.py
│   ├── module_nmap.py
│   ├── module_oneforall.py
│   ├── module_whatweb.py
│   └── sql.py
├── install.sh      install script for installing modules (dependencies and so on ..)
├── output      all modules tmp file/result file will be put in there
│   ├── dirsearch
│   ├── EyeWitness
│   ├── nmap
│   ├── oneforall
│   └── whatweb
├── print_state.py
├── readme.md
├── reconFramework.py       the main file
├── requirements.txt
├── setup_database.py       script for database setup
└── tools       directory for putting tools here
    ├── dirsearch
    ├── EyeWitness
    ├── EyeWitness.bak
    ├── masmap_script
    └── OneForAll
```

## How to write my own modules?

In file base_class.py I have defined a metaclass named Module, and all you need to do is to write a class inherit the Module class and implement these abstract method

```python
class Module(metaclass=ABCMeta):
    def __init__(self, pipe=None):
        self.pipe_list = [] # where the result data will be sent
        self.task_list = [] # get tasks from here

    @abstractmethod
    def exec(self):
        """ start to work """
        pass

    @abstractmethod
    def get_output(self):
        """ get the result data """
        pass

    @abstractmethod
    def update_database(self, data):
        """data is the object that the get_output() return"""
        pass
```

A Pipe object is the object between module and module, which get the result data from the last module and send it to the next module, and you can process the data while the data is being transfered.

```python
from framework_modules.module_nmap import Nmap
from framework_modules.module_check_cdn import CheckCDN
nmap = Nmap(max_workers=16)
check_cdn = CheckCDN()
# check cdn -> nmap
check_cdn2nmap = Pipe(
    '''you can write a function with one parameter as data input to process the data'''
    func=lambda data: [
        data[hostname]["ip_address"]
        for hostname in data
        if not data[hostname]["use_CDN"]
    ],
    module=nmap, # the module which data will be sent as task
)
# add the Pipe object to the module's pipe list so that the reuslt data will be sent to pipe
check_cdn.register_pipe(check_cdn2nmap) 
```

## Contribution

feel free to submit issue and it will be my pleasure if you contribute your code to this project


## To-do list

- finish BruteSpray module
- command line interface