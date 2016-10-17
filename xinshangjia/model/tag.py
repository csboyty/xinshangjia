# coding:utf-8

from ..core import db
from ..sqlalchemy_helper import AsDictMixin

tag_include = ['id', 'name']


class Tag(db.Model, AsDictMixin):
    __tablename__ = "tag"
    __dictfields__ = dict(include=tag_include)

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)

    def __eq__(self, other):
        if isinstance(other, Tag) and getattr(other, 'name', None):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)