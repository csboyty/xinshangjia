# coding:utf-8

from flask_user.signals import user_logged_out, user_logged_in
from .core import redis_cache


@user_logged_out.connect
def on_user_logged_out(app, user=None):
    from .service import userService

    if user.is_authenticated() and hasattr(user, 'id'):
        redis_cache.delete_memoized(userService.user_by_id, user.id)








