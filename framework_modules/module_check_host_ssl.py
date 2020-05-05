import httpx
import asyncio

# import requests
import sys
import os
import inspect
import logging


from .base_class import Module
from .sql import SqlHelper

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
basedir = os.path.dirname(currentdir)
dirsearch_path = os.path.join(basedir, "tools", "dirsearch", "dirsearch.py")
outputdir = os.path.join(basedir, "output", "dirsearch")
if not os.path.exists(outputdir):
    os.mkdir(outputdir)


class CheckHostSSL(Module):
    """ check if a hostname support http or https
    
    input: string hostname
    
    output: list of url
    
    e.g.

    ["https://www.baidu.com","http://www.google.com"]"""

    def __init__(self):
        super().__init__()
        self.result = list()

    def exec(self):
        # executor = ThreadPoolExecutor(max_workers=16)
        # for hostname in self.task_list:
        #     executor.submit(self.check_ssl, hostname)
        # executor.shutdown(wait=True)
        asyncio.run(self.check_all())

    async def check_all(self):
        self.client = httpx.AsyncClient()
        task_iterator = iter(self.task_list)
        tmp_list = []
        try:
            while True:
                while len(tmp_list) < 32:
                    tmp_list.append(next(task_iterator))
                await asyncio.gather(
                    *[self.check_ssl(hostname) for hostname in tmp_list]
                )
                tmp_list = []
        except StopIteration:
            await asyncio.gather(*[self.check_ssl(hostname) for hostname in tmp_list])
        await self.client.aclose()

    async def check_ssl(self, hostname):
        self.logger.info(self.__class__.__name__ + " check host: " + hostname)
        try:
            await self.client.get("https://" + hostname)
            url = "https://" + hostname
        except Exception as e:
            # print(e)
            try:
                await self.client.get("http://" + hostname)
                url = "http://" + hostname
            except:
                return
        self.result.append(url)
        self.logger.info(self.__class__.__name__ + " add url to result: " + url)

    def get_output(self):
        self.logger.info(
            self.__class__.__name__ + " result size: " + str(len(self.result))
        )
        return self.result

    def empty(self):
        self.result = list()

    def update_database(self, data):
        pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
    )
    # check_cdn_ssl = CheckHostSSL()
    # check_cdn_ssl.add_task("www.baidu.com")
    # check_cdn_ssl.add_task("weibo.com")
    # check_cdn_ssl.run()
