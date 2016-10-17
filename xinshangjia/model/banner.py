# coding:utf-8

from ..core import db
from ..sqlalchemy_helper import AsDictMixin, TimestampMixin

banner_status_disable = 0
banner_status_enable = 1


class Banner(db.Model, AsDictMixin, TimestampMixin):
    __tablename__ = "banner"
    __dictfields__ = dict(include=["id", "caption", "image_url", "link_url", "ordering", "status", "locale"])

    id = db.Column(db.Integer(), primary_key=True)
    caption = db.Column(db.Unicode(64), nullable=False)
    image_url = db.Column(db.String(256), nullable=False)
    link_url = db.Column(db.String(256), nullable=True)
    ordering = db.Column(db.SmallInteger(), nullable=False)
    status = db.Column(db.SmallInteger(), nullable=False, default=banner_status_disable)
    locale = db.Column(db.String(10), nullable=False)

    def __eq__(self, other):
        if isinstance(other, Banner) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)
