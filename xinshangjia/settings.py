# coding:utf-8

import os

basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

SQLALCHEMY_ECHO = False

CELERY_BROKER_URL = "redis://localhost:6379/10"
CELERY_RESULT_BACKEND = "redis://localhost:6379/11"
CELERY_DEFAULT_QUEUE = "xinshangjia"
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

qiniu_bucket = "xinshangjia"
qiniu_baseurl = "http://7xi5a6.com5.z0.glb.clouddn.com/"
qiniu_ak = "Q-DeiayZfPqA0WDSOGSf-ekk345VrzuZa_6oBrX_"
qiniu_sk = "fIiGiRr3pFmHOmBDR2Md1hTCqpMMBcE_gvZYMzwD"

system_default_tz_name = u'Asia/Shanghai'

account_default_tz_name = u'Asia/Shanghai'
account_default_country = u'cn'
account_default_locale = u'zh'

artifact_thumbnails = ['300x300', '200x200', '100x100']
asset_thumbnails = ['500x']

languages = ['zh', 'en']

default_lanuage = 'en'

artifact_per_page = 100
designer_per_page = 100
designer_artifact_per_page = 100

USER_AFTER_LOGIN_ENDPOINT = 'app.user'
USER_AFTER_LOGOUT_ENDPOINT = 'app.index'
USER_UNAUTHORIZED_ENDPOINT = 'app.unauthorized_page'
USER_APP_NAME = u'New Channel'




