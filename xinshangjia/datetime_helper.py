# coding:utf-8

import datetime
import pytz
from pytz import country_timezones
from flask import g
from flask.ext.login import current_user
from werkzeug.local import LocalProxy

from .settings import system_default_tz_name

local_timezone = pytz.timezone(system_default_tz_name)
utc_timezone = pytz.utc
current_timezone = LocalProxy(lambda: _get_tz())


def _get_tz(tz_name=None):
    tz = getattr(g, "current_timezone", None)
    if tz is None:
        if not tz_name:
            if current_user and current_user.is_authenticated():
                user = current_user._get_current_object()
            if user.account is not None and user.account.tz:
                tz_name = user.account.tz
            else:
                tz_name = system_default_tz_name

        if tz_name == system_default_tz_name:
            tz = local_timezone
        else:
            try:
                tz = pytz.timezone(tz_name)
            except pytz.UnknownTimeZoneError:
                tz = local_timezone

        g.current_timezone = tz
    return tz


def parse_local_to_utc_datetime(dt, tz_name=None, fmt="%Y-%m-%d %H:%M:%S"):
    tz = _get_tz(tz_name)
    return utc_timezone.normalize(datetime.datetime.strptime(dt, fmt).replace(tzinfo=tz))


def format_utc_to_local_datetime(dt, tz_name=None, fmt="%Y-%m-%d %H:%M:%S"):
    tz = _get_tz(tz_name)
    return tz.normalize(dt.replace(tzinfo=utc_timezone)).strftime(fmt)


def get_tz_by_country(country_code):
    tz_list = country_timezones[country_code]
    if tz_list:
        return tz_list[0]
    else:
        return system_default_tz_name


def now():
    return datetime.datetime.utcnow().replace(tzinfo=utc_timezone)