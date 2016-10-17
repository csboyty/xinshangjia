# coding:utf-8

import base64
import functools
import hashlib
import logging
import string

from itsdangerous import PY2
from werkzeug.contrib.cache import RedisCache as BaseRedisCache
from redis import from_url as redis_from_url
from flask import current_app, request
from redisco.containers import List, Set, SortedSet, Hash

logger = logging.getLogger(__name__)

# Used to remove control characters and whitespace from cachekeys
valid_chars = set(string.ascii_letters + string.digits + '_.')
delchars = ''.join(c for c in map(chr, range(256)) if c not in valid_chars)
if PY2:
    null_control = (None, delchars)
else:
    null_control = (dict((k, None) for k in delchars),)


def function_namespace(f):
    """
    Attempts to return unique namespace for function
    """
    module = f.__module__
    ns = "{0}:{1}".format(module, f.__name__)
    return base64.b64encode(hashlib.md5(ns).digest())[:8]


class RedisCache(object):
    def __init__(self, app=None, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be  an instance of dict or None")
        self.config = config
        self.app = app
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be  an instance of dict or None")
        base_config = app.config.copy()
        if self.config:
            base_config.update(self.config)
        if config:
            base_config.update(config)
        config = base_config

        config.setdefault('CACHE_DEFAULT_TIMEOUT', 24 * 60 * 60)  # default 1 day
        config.setdefault('CACHE_THRESHOLD', 500)
        config.setdefault('CACHE_KEY_PREFIX', 'rc_')
        config.setdefault('CACHE_DIR', None)
        config.setdefault('CACHE_OPTIONS', None)
        config.setdefault('CACHE_ARGS', [])

        self._set_cache(app, config)

    def _set_cache(self, app, config):
        cache_args = config['CACHE_ARGS'][:]
        cache_options = {'default_timeout': config['CACHE_DEFAULT_TIMEOUT']}

        if config['CACHE_OPTIONS']:
            cache_options.update(config['CACHE_OPTIONS'])

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions.setdefault('cache', {})
        app.extensions['cache'][self] = _redis(app, config, cache_args, cache_options)

    @property
    def _cache(self):
        app = self.app or current_app
        return app.extensions['cache'][self]

    @property
    def _containers(self):
        if hasattr(self._cache, 'containers'):
            containers = getattr(self._cache, 'containers')
        else:
            self._cache.containers = containers = {}
        return containers

    def _get_container(self, key, expire_seconds, factory_method):
        containers = self._containers
        if key in containers:
            container = containers.get(key)
        else:
            redis_key = self._cache.key_prefix + ":" + key
            container = containers[key] = factory_method(key=redis_key, db=self._cache._client)
        if expire_seconds >= 0:
            container.set_expire(expire_seconds)
        return container

    def delete_container(self, key):
        containers = self._containers
        if key in containers:
            del containers[key]
            redis_key = self._cache.key_prefix + ":" + key
            self._cache._client.delete(redis_key)

    def get_list(self, key, expire_seconds=-1):
        return self._get_container(key, expire_seconds, List)

    def get_set(self, key, expire_seconds=-1):
        return self._get_container(key, expire_seconds, Set)

    def get_sorted_set(self, key, expire_seconds=-1):
        return self._get_container(key, expire_seconds, SortedSet)

    def get_hash(self, key, expire_seconds=-1):
        return self._get_container(key, expire_seconds, Hash)

    def get(self, *args, **kwargs):
        return self._cache.get(*args, **kwargs)

    def set(self, *args, **kwargs):
        self._cache.set(*args, **kwargs)

    def add(self, *args, **kwargs):
        self._cache.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._cache.delete(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        self._cache.delete_many(*args, **kwargs)

    def clear(self):
        self._cache.clear()

    def get_many(self, *args, **kwargs):
        return self._cache.get_many(*args, **kwargs)

    def set_many(self, *args, **kwargs):
        self._cache.set_many(*args, **kwargs)

    def cache(self, timeout=None, key_prefix='view/%s', unless=None):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # : Bypass the cache entirely.
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = decorated_function.make_cache_key(*args, **kwargs)
                    rv = self._cache.get(cache_key)
                except Exception as e:
                    if current_app.debug:
                        raise
                    logger.exception("Exception possibly due to cache backend.", e)
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)
                    try:
                        self._cache.set(cache_key, rv, timeout=decorated_function.cache_timeout)
                    except Exception as e:
                        if current_app.debug:
                            raise
                        logger.exception("Exception possibly due to cache backend.", e)
                        return f(*args, **kwargs)
                return rv

            def make_cache_key(*args, **kwargs):
                if callable(key_prefix):
                    cache_key = key_prefix()
                elif '%s' in key_prefix:
                    cache_key = key_prefix % request.path
                else:
                    cache_key = key_prefix

                return cache_key

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = make_cache_key

            return decorated_function

        return decorator

    def memoize(self, timeout=None, unless=None):
        def memoize(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # : bypass cache
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = decorated_function.make_cache_key(f, *args, **kwargs)
                    rv = self._cache.get(cache_key)
                except Exception as e:
                    if current_app.debug:
                        raise
                    logger.exception("Exception possibly due to cache backend.", e)
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)
                    try:
                        self._cache.set(cache_key, rv, timeout=decorated_function.cache_timeout)
                    except Exception as e:
                        if current_app.debug:
                            raise
                        logger.exception("Exception possibly due to cache backend.", e)
                return rv

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = _memoize_make_cache_key()
            return decorated_function

        return memoize

    def delete_memoized(self, f, *args, **kwargs):
        if not callable(f):
            raise DeprecationWarning(
                "Deleting cached object by relative name is no longer reliable, please switch to a function reference")

        try:
            cache_key = f.make_cache_key(f.uncached, *args, **kwargs)
            if not args and not kwargs:
                self._cache.delete_by_pattern(cache_key + "*")
            else:
                self._cache.delete(cache_key)

        except Exception as e:
            if current_app.debug:
                raise
            logger.exception("Exception possibly due to cache backend.", e)


def _memoize_make_cache_key():
    def make_cache_key(f, *args, **kwargs):
        fname = function_namespace(f)
        if args and getattr(args[0], f.__name__, None):
            args_without_self = args[1:]
        else:
            args_without_self = args

        if not args_without_self and not kwargs:
            cache_key = ""
        else:
            cache_key = hashlib.md5()
            cache_key.update("{0}{1}".format(args_without_self, kwargs).encode('utf-8'))
            cache_key = base64.b64encode(cache_key.digest())[:8]
            cache_key = cache_key.decode('utf-8')

        return fname + ":" + cache_key

    return make_cache_key


class _RedisCache(BaseRedisCache):
    def __init__(self, host='localhost', port=6379, password=None,
                 db=0, default_timeout=300, key_prefix=None):
        BaseRedisCache.__init__(self, host=host, port=port, password=password, db=db, default_timeout=default_timeout,
                                key_prefix=key_prefix)

    def delete_by_pattern(self, pattern):
        if pattern:
            keys = self._client.keys(self.key_prefix + pattern if self.key_prefix else pattern)
            return self._client.delete(*keys) if keys else []
        else:
            return []


def _redis(app, config, args, kwargs):
    kwargs.update(dict(
        host=config.get('CACHE_REDIS_HOST', 'localhost'),
        port=config.get('CACHE_REDIS_PORT', 6379)
    ))
    password = config.get('CACHE_REDIS_PASSWORD')
    if password:
        kwargs['password'] = password

    key_prefix = config.get('CACHE_KEY_PREFIX')
    if key_prefix:
        kwargs['key_prefix'] = key_prefix

    default_timeout = config.get('CACHE_DEFAULT_TIMEOUT')
    if default_timeout:
        kwargs['default_timeout'] = int(default_timeout)

    db_number = config.get('CACHE_REDIS_DB')
    if db_number:
        kwargs['db'] = db_number

    redis_url = config.get('CACHE_REDIS_URL')
    if redis_url:
        kwargs['host'] = redis_from_url(redis_url, db=kwargs.pop('db', None), )

    return _RedisCache(*args, **kwargs)

