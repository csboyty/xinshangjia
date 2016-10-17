# coding:utf-8

import pkgutil
import importlib
import datetime
import functools
from flask import Blueprint, current_app, make_response, request, json
from flask.json import JSONEncoder as BaseJSONEncoder

from .sqlalchemy_helper import AsDictMixin
from . import datetime_helper


def register_blueprints(app, package_name, package_path):
    for _, name, _ in pkgutil.iter_modules(package_path):
        try:
            m = importlib.import_module("%s.%s" % (package_name, name))
            for item in dir(m):
                item = getattr(m, item)
                if isinstance(item, Blueprint):
                    app.register_blueprint(item)
        except Exception, e:
            print e


class JSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, AsDictMixin):
            return obj.as_dict()
        if isinstance(obj, datetime.datetime):
            return datetime_helper.format_utc_to_local_datetime(obj, fmt="%Y-%m-%d %H:%M:%S")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        return super(JSONEncoder, self).default(obj)


def json_response(success=True, **kwargs):
    return current_app.response_class(
        json.dumps(dict(success=success, **kwargs), cls=JSONEncoder, indent=None if request.is_xhr else 2),
        mimetype='application/json')


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, datetime.timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return functools.update_wrapper(wrapped_function, f)

    return decorator