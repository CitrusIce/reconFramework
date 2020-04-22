import pymysql
import sys

if __name__ == "__main__":
    import os
    import inspect

    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))
    )
    basedir = os.path.dirname(currentdir)
    sys.path.insert(1, basedir)


import framework_config

# from config import *
import logging


class SqlHelper:
    def __init__(self):
        self.db = pymysql.connect(
            host=framework_config.mysql_host,
            port=framework_config.mysql_port,
            user=framework_config.mysql_user,
            password=framework_config.mysql_passwd,
            database=framework_config.mysql_db,
        )
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()

    def update(self, table, primary_dict, data=None):
        if not isinstance(primary_dict, dict):
            raise TypeError("primary_dict should be dict!")
        if data is None:
            # dynamic construct sql
            sql = "INSERT IGNORE INTO {table}({primary_key}) VALUES ({value});".format(
                table=table,
                primary_key=",".join(list(primary_dict.keys())),
                value=",".join(len(primary_dict) * ["%s"]),
            )
            self.cursor.execute(sql, tuple(primary_dict.values()))
        elif isinstance(data, dict):
            for key in data:
                sql = """INSERT INTO {table} ({primary_key},{key}) 
                    VALUES ({value},%s) 
                    ON DUPLICATE KEY UPDATE {key}=%s;""".format(
                    table=table,
                    primary_key=",".join(list(primary_dict.keys())),
                    key=key,
                    value=",".join(len(primary_dict) * ["%s"]),
                )
                try:
                    self.cursor.execute(
                        sql, tuple(primary_dict.values()) + (data[key], data[key])
                    )
                # logging.debug("execute sql: " + sql)
                # logging.debug(primary_key_value + " " + data[key])
                except Exception as e:
                    logging.error(
                        "Exception raised while inserting key: "
                        + key
                        + ", data:"
                        + data[key]
                        + str(e)
                    )
                # result = self.cursor.fetchone()
                # logging.debug(""+result)
        else:
            logging.critical("data should be dict or None")
            raise Exception("data: invalid format")
        self.db.commit()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout),],
    )

    sql = SqlHelper()
    # 使用 execute()  方法执行 SQL 查询
    sql.update("project_assets", {"domain": "www.google.com1"})
    sql.update("project_assets", {"domain": "www.google.com"}, {"project_name": "bbb"})
