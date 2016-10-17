# coding:utf-8

DEBUG = True

SECRET_KEY = 'xinshangjia-skey'
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://dbuser:dbpassword@192.168.2.104/xinshangjia"

MAIL_DEFAULT_SENDER = "asset_hub@qq.com"
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
MAIL_USERNAME = "asset_hub@qq.com"
MAIL_PASSWORD = "asset111222"

CACHE_REDIS_HOST = "localhost"
CACHE_REDIS_PORT = 6379
CACHE_KEY_PREFIX = "xsj:"
CACHE_REDIS_DB = 4
CACHE_DEFAULT_TIMEOUT = 1800