# reconFramework

现在有很多信息收集工具，但是没有一款可以做到能自动收集一个目标的所有信息，同时这也是不可能的，但是我们可以将这些工具组装起来，成为一个全新的工具，使我们信息收集的工作变得自动化，因此我产生了写这个框架的念头。

这个工具的主要思想就是将其他工具封装为模块，并将这些模块的输入输出相连，达到自动信息收集，最终收集到的数据将存储在数据库中。

## 安装

```bash
git clone https://github.com/CitrusIce/reconFramework.git
cd reconFramework
./install.sh

# after change database config in framework_config.py
python3 setup_database.py
```

## 如何使用

我还没有将这个项目写完，因此还有没有cli，如果要使用就需要修改reconFramework.py的代码，但是不需要改太多，只用将最下面的域名修改为目标域名就可以运行了

运行后它将为你做这些事

- 使用oneforall 收集子域名
- 使用nmap扫描一些常用端口并探测服务
- 使用whatweb 扫描web服务的指纹 
- 使用dirsearch 扫描web路径
- 使用Eyewitness 网页截图

## requirements

- python >= 3.8

## module

这个框架已经预置了一些我封装的模块

- [dirsearch](https://github.com/maurosoria/dirsearch)
- [EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness)
- [Nmap](https://nmap.org/)
- [oneforall](https://github.com/shmilylty/OneForAll)
- [whatweb](https://github.com/urbanadventurer/WhatWeb)
- [BruteSpray](https://github.com/x90skysn3k/brutespray) (still working on it)
- check_cdn 
- check_host_ssl

感谢开发这些工具的开发者！

## 目录结构

```
.
├── clean_database.py       删除数据库所有数据的脚本
├── framework_config.py     框架设置文件
├── framework_modules       框架所有模块存放在这里
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
├── install.sh      安装脚本 (安装需要的工具以及依赖)
├── output      所有模块输出的临时文件、结果文件会被放在这里
│   ├── dirsearch
│   ├── EyeWitness
│   ├── nmap
│   ├── oneforall
│   └── whatweb
├── print_state.py
├── reconFramework.py       主文件
├── requirements.txt
├── setup_database.py       设置数据库的脚本
└── tools       模块所需要的工具放在这
    ├── dirsearch
    ├── EyeWitness
    ├── EyeWitness.bak
    ├── masmap_script
    └── OneForAll
```

## 如何写一个模块

在文件 base_class.py 中我定义了一个元类Module，你只需要写一个class继承这个Module类同时实现其中的抽象方法就可以了

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

Pipe对象是模块间的媒介，用于模块间数据的传输。它接收上一个模块的结果并将这些数据作为task送到下一个模块，同时你可以在数据被传输的时候对数据进行一些处理

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

## 贡献

欢迎向本项目提交issue以及贡献代码

## To-do list

- 完成BruteSpray模块
- 写一个命令行界面
