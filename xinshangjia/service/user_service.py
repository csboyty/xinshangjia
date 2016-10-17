# coding:utf-8

from ..core import BaseService, redis_cache
from ..model import User
from ..utils import dotdict


class UserService(BaseService):
    __model__ = User

    @redis_cache.memoize(timeout=1800)
    def user_by_id(self, user_id):
        user = self.get(user_id)
        if user:
            return dotdict(user.as_dict())

    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


userService = UserService()