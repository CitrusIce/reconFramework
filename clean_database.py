import pymysql
from framework_config import *

db = pymysql.connect(
    host=mysql_host,
    port=mysql_port,
    user=mysql_user,
    password=mysql_passwd,
    database=mysql_db,
)
cursor = db.cursor()
# create database
cursor.execute("delete from project_assets")
cursor.execute("delete from server_information")
cursor.execute("delete from web_path_information")
cursor.execute("delete from web_service")
db.commit()
db.close()
