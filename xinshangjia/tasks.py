# coding:utf-8


from celery.utils.log import get_task_logger

from .factory import create_celery_app
from .qinius import mk_image_thumbnail, rm_image_thumbnail, rm_key


logger = get_task_logger(__name__)
celery_app = create_celery_app()


@celery_app.task(bind=True)
def gen_qiniu_thumbnail(self, key_or_url, image_sizes):
    # print "task gen_qiniu_thumbnail", key_or_url, image_sizes
    try:
        mk_image_thumbnail(key_or_url=key_or_url, image_sizes=image_sizes)
    except Exception as exc:
        logger.error("gen_qiniu_thumbnail error, key_or_url:" + key_or_url, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True)
def remove_qiniu_thumbnail(self, key_or_url, image_sizes):
    # print "task remove_qiniu_thumbnail", key_or_url, image_sizes
    try:
        rm_image_thumbnail(key_or_url=key_or_url, image_sizes=image_sizes)
    except Exception as exc:
        logger.error("remove_qiniu_thumbnail error, key_or_url:" + key_or_url, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True)
def remove_qiniu_key(self, key_or_url):
    # print "task remove_qiniu_key"
    try:
        rm_key(key_or_url)
    except Exception as exc:
        logger.error("remove_qiniu_key error, key_or_url:" + key_or_url, exc)
        self.retry(exc=exc)
