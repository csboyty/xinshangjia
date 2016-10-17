# coding:utf-8

from flask.ext.script import Command
from ..core import redis_cache
from ..model import Account


class InitAccountEmailsCommand(Command):

    def run(self):
        account_emails = redis_cache.get_set('account_emails')
        for (email,) in Account.query.with_entities(Account.email).all():
            account_emails.add(email)
