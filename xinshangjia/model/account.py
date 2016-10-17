# coding:utf-8

from ..core import db
from ..sqlalchemy_helper import TimestampMixin, AsDictMixin
from .. import country_helper

account_type_designer = 1
account_type_user = 2
account_type_enterprise = 3

class UserAccount(db.Model):
    __tablename__ = "user_account"

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), primary_key=True)
    account_id = db.Column(db.Integer(), db.ForeignKey('account.id', ondelete='cascade'), primary_key=True)


class Account(db.Model, TimestampMixin, AsDictMixin):
    __tablename__ = "account"
    __dictfields__ = dict(include=["id", "type", "email", "first_name", "last_name", "nick_name", "image_url",
                                   "country", "country_name", "tz", "description"])

    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.SmallInteger(), nullable=False, default=account_type_designer)
    email = db.Column(db.Unicode(64), nullable=False, unique=True)
    first_name = db.Column(db.Unicode(32), nullable=False, server_default='')
    last_name = db.Column(db.Unicode(32), nullable=False, server_default='')
    nick_name = db.Column(db.Unicode(32), nullable=False, server_default='')
    image_url = db.Column(db.String(256), nullable=True)
    country = db.Column(db.String(2), nullable=False, default='CN')
    locale = db.Column(db.String(10), nullable=False, default='zh')
    description = db.Column(db.UnicodeText, nullable=True)
    tz = db.Column(db.String(32), nullable=False)
    secret = db.relationship('Secret', uselist=False)

    # def __getattr__(self, name):
    # # intercept UserInfo fields
    #     if hasattr(UserInfo, name):
    #         return getattr(self.user_info, name) if self.user_info else None
    #     return object.__getattribute__(self, name)

    @property
    def country_name(self):
        return country_helper.code_to_name(self.country)

    @property
    def secret_info(self):
        return self.secret.as_dict() if self.secret else {}

    def __eq__(self, other):
        if isinstance(other, Account) and self.email == getattr(other, 'email', None):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.email)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)


class Secret(db.Model, AsDictMixin):
    __tablename__ = "account_secret"
    __dictfields__ = dict(include=["credentials_url", "bank", "account_name", "account_no", "tel", "address"])

    account_id = db.Column(db.Integer(), db.ForeignKey('account.id', ondelete='CASCADE'), primary_key=True)
    credentials_url = db.Column(db.String(256), nullable=False, server_default='')
    bank = db.Column(db.String(256), nullable=False, server_default='')
    account_name = db.Column(db.String(128), nullable=False, server_default='')
    account_no = db.Column(db.String(32), nullable=False, server_default='')
    tel = db.Column(db.String(32), nullable=False, server_default='')
    address = db.Column(db.String(256), nullable=False, server_default='')

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)

