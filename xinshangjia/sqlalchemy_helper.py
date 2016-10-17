# coding:utf-8


import sqlalchemy as sa
from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.orm import attributes
from sqlalchemy_utils import JSONType, batch_fetch
from dictalchemy.utils import asdict
import datetime


from . import datetime_helper


class Deleted(object):
    deleted = sa.Column(sa.Boolean(), default=False, nullable=False)


class AsDictMixin(object):
    __dictfields__ = None

    def as_dict(self):
        return asdict(self, **self.__dictfields__)


class UTCDateTime(sa.types.TypeDecorator):
    impl = sa.types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None and value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
            return value.astimezone(datetime_helper.utc_timezone)
        else:
            raise ValueError("The datetime value is naive", value)

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime.datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=datetime_helper.utc_timezone)


class TimestampMixin(object):
    created = sa.Column(UTCDateTime, default=datetime_helper.now, nullable=False)
    updated = sa.Column(UTCDateTime, default=datetime_helper.now, nullable=True)


@sa.event.listens_for(TimestampMixin, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated = datetime_helper.now()


class DeletedExtension(SessionExtension):
    def before_flush(self, session, flush_context, instances):
        for instance in session.deleted:
            if not isinstance(instance, Deleted):
                continue

            if not attributes.instance_state(instance).has_identity:
                continue

            instance.deleted = True
            session.add(instance)


