# coding:utf-8

from ..core import db
from ..sqlalchemy_helper import UTCDateTime, JSONType, AsDictMixin
from ..datetime_helper import now


class CeleryTaskLog(db.Model, AsDictMixin):
    __tablename__ = "celery_task_log"
    __dictfields__ = dict(include=["id", "name", "args", "kwargs", "retval", "exception", "status", "create_at"])

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    args = db.Column(JSONType, nullable=True)
    kwargs = db.Column(JSONType, nullable=True)
    retries = db.Column(db.Integer(), default=0)
    retval = db.Column(db.Unicode(256), nullable=True)
    exception = db.Column(db.Unicode(512), nullable=True)
    status = db.Column(db.SmallInteger(), nullable=True, default=0)  # -2:retry, -1:failure, 1:success,
    create_at = db.Column(UTCDateTime, default=now)


