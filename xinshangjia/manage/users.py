# coding:utf-8
from __future__ import print_function
from flask.ext.script import Command, prompt, prompt_pass

from ..datetime_helper import now
from ..core import db
from ..model import User

import hashlib


def hash_password(password):
    _md5 = hashlib.md5()
    _md5.update(password)
    return _md5.hexdigest()


class CreateUserCommand(Command):
    def run(self):
        email = prompt('Email')
        password = prompt_pass('Password')
        password_confirm = prompt_pass('Confirm Password')
        active = bool(prompt('Actvice immediately', default='True'))
        role = prompt('Role', default='admin')
        if password == password_confirm:
            user = User(email=email, password=hash_password(password), confirmed_at=now(), active=active, role=role)
            db.session.add(user)
            db.session.commit()









