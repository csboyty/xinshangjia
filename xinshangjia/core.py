# coding: utf-8

from flask_sqlalchemy import SQLAlchemy
from flask import g, abort, request
from flask_user import current_user

from .sqlalchemy_helper import DeletedExtension
from .redis_cache import RedisCache
from .settings import languages, default_lanuage


db = SQLAlchemy(session_options={
    "extension": [DeletedExtension()],
    'expire_on_commit': False
})
redis_cache = RedisCache()


class AppError(Exception):
    def __init__(self, message, error_code, *args):
        self.message = message
        self.error_code = error_code
        super(AppError, self).__init__(message, error_code, *args)


def after_commit(f):
    callbacks = getattr(g, 'on_commit_callbacks', None)
    if callbacks is None:
        g.on_commit_callbacks = callbacks = []
    callbacks.append(f)
    return f


def get_locale():
    locale = getattr(g, 'locale', None)
    if locale is None:
        user = current_user
        if user.is_authenticated() and user.account is not None:
            locale = user.account.locale
        if not locale:
            locale = request.accept_languages.best_match(languages)
        if not locale or not (locale in languages):
            locale = default_lanuage

        g.locale = locale
    return locale


class BaseService(object):
    __model__ = None

    def save(self, model):
        db.session.add(model)
        db.session.flush()
        return model

    def get(self, model_id):
        if hasattr(self.__model__, 'deleted'):
            return self.__model__.query.filter(self.__model__.id == model_id, self.__model__.deleted == False).first()
        else:
            return self.__model__.query.get(model_id)

    def get_multi(self, model_ids):
        if hasattr(self.__model__, 'deleted'):
            return self.__model__.filter(self.__model__.id.in_(model_ids), self.__model__.deleted == False).all()
        else:
            return self.__model__.filter(self.__model__.id.in_(model_ids)).all()

    def get_all(self, orders=[]):
        if not orders:
            orders = [self.__model__.id.asc()]
        if hasattr(self.__model__, 'deleted'):
            return self.__model__.query.filter(self.__model__.deleted == False).order_by(*orders).all()
        else:
            return self.__model__.query.order_by(*orders).all()

    def get_or_404(self, model_id):
        rv = self.get(model_id)
        if rv is None:
            abort(404)
        return rv

    def delete(self, model):
        db.session.delete(model)
        db.session.flush()


    def find_id_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        if hasattr(self.__model__, 'deleted'):
            filters.append(self.__model__.deleted == False)

        data = self.__model__.query.with_entities(self.__model__.id).filter(*filters). \
            order_by(*orders).offset(offset).limit(limit).all()

        return [id_ for (id_, ) in data]


    def paginate_id_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        if hasattr(self.__model__, 'deleted'):
            filters.append(self.__model__.deleted == False)

        ids = []
        count = self.__model__.query.with_entities(db.func.count(self.__model__.id)).filter(*filters).scalar()
        if count:
            if offset is None and limit is None:
                data = self.__model__.query.with_entities(self.__model__.id).filter(*filters). \
                    order_by(*orders).all()
            else:
                data = self.__model__.query.with_entities(self.__model__.id).filter(*filters). \
                    order_by(*orders).offset(offset).limit(limit).all()

            ids = [id_ for (id_, ) in data]

        return count, ids

    def paginate_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        if hasattr(self.__model__, 'deleted'):
            filters.append(self.__model__.deleted == False)

        data = []
        count = self.__model__.query.with_entities(db.func.count(self.__model__.id)).filter(*filters).scalar()
        if count:
            if offset is None and limit is None:
                data = self.__model__.query.filter(*filters).order_by(*orders).all()
            else:
                data = self.__model__.query.filter(*filters).order_by(*orders).offset(offset).limit(limit).all()

        return count, data
