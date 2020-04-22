import pymysql
from framework_config import *

db = pymysql.connect(
    host=mysql_host,
    port=mysql_port,
    user=mysql_user,
    password=mysql_passwd,
    # database=mysql_db,
)
cursor = db.cursor()
# create database
cursor.execute("CREATE DATABASE IF NOT EXISTS %s;" % mysql_db)
cursor.execute("use %s" % mysql_db)

# create table project_assets
cursor.execute(
    """CREATE TABLE IF NOT EXISTS `project_assets`(
   `domain` VARCHAR(255) PRIMARY KEY,
   `project_name` VARCHAR(100),
   `ip_address` VARCHAR(255),
   `use_CDN` TINYINT(1)
) CHARSET=utf8"""
)
# create table server_information
cursor.execute(
    """CREATE TABLE IF NOT EXISTS `server_information`(
   `ip_address` VARCHAR(50) ,
   `open_port_id` INT ,
   `port_service` VARCHAR(1024),
	 PRIMARY KEY (ip_address,open_port_id)
) CHARSET=utf8"""
)
# create table web_service
cursor.execute(
    """CREATE TABLE IF NOT EXISTS `web_service`(
   `url` VARCHAR(255) PRIMARY KEY ,
   `web_fingerprint` VARCHAR(4095) ,
   `title` VARCHAR(255),
	 `screenshot_path` VARCHAR(255)
) CHARSET=utf8"""
)
# create table web_path_information
cursor.execute(
    """CREATE TABLE IF NOT EXISTS `web_path_information`(
   `url` VARCHAR(255)  ,
   `available_path` VARCHAR(255),
	 PRIMARY KEY(url,available_path),
   `state_code` int,
	 `content_length` int,
	 `redirect` VARCHAR(4096)
) CHARSET=utf8"""
)


db.commit()
# close database
db.close()
