# coding:utf-8

from flask_user import UserMixin

from ..core import db
from ..sqlalchemy_helper import AsDictMixin

user_role_admin = 'admin'
user_role_designer = 'designer'
user_role_user = 'user'


class User(db.Model, UserMixin, AsDictMixin):
    __tablename__ = "user"
    __dictfields__ = dict(include=["id", "email", "username", "confirmed_at", "active", "role"])

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(64), nullable=False, unique=True)
    username = db.synonym("email")
    confirmed_at = db.Column(db.DateTime(), nullable=True)
    password = db.Column(db.String(128), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='1')
    role = db.Column(db.String(16), nullable=False)
    account = db.relationship("Account", secondary="user_account", uselist=False)

    def has_roles(self, *requirements):

        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                if self.role in tuple_of_role_names:
                    return True
            else:
                # this is a role_name requirement
                role_name = requirement
                # the user must have this role
                if role_name == self.role:
                    return True  # role_name requirement failed: return False

        # All requirements have been met: return True
        return True

    def __eq__(self, other):
        if isinstance(other, User) and self.email == getattr(other, 'email', None):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.email)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)


