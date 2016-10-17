# coding:utf-8

from sqlalchemy.orm import joinedload as sa_joinedload
from ..core import BaseService, redis_cache, after_commit, db
from ..model import Account, Secret
from ..settings import account_default_country, account_default_locale, account_default_tz_name



class AccountService(BaseService):
    __model__ = Account

    @redis_cache.memoize()
    def account_by_account_id(self, account_id):
        account = self.get(account_id)
        return account.as_dict() if account else None

    def create_account(self, account_type, **kwargs):
        account = Account(type=account_type)
        account.email = kwargs['email']
        account.first_name = kwargs.get('first_name', None)
        account.last_name = kwargs.get('last_name', None)
        account.nick_name = kwargs.get('nick_name', None)
        account.image_url = kwargs.get('image_url', None)
        account.description = kwargs.get('description', None)
        account.country = kwargs.get('country', account_default_country)
        account.locale = kwargs.get('locale', account_default_locale)
        account.tz = kwargs.get('tz', account_default_tz_name)
        account.secret = Secret(tel=kwargs.get('tel', None), address=kwargs.get('address', None))
        self.save(account)

        def do_after_commit():
            redis_cache.delete_memoized(accountService.account_by_account_id, account.id)
            redis_cache.get_set('account_emails').add(account.email)

        after_commit(do_after_commit)
        return account

    def update_account(self, account_id, **kwargs):
        account = self.get_or_404(account_id)
        origin_account_email = account.email
        account.email = kwargs['email']
        account.first_name = kwargs.get('first_name', None)
        account.last_name = kwargs.get('last_name', None)
        account.nick_name = kwargs.get('nick_name', None)
        account.image_url = kwargs.get('image_url', None)
        account.description = kwargs.get('description', None)
        account.country = kwargs.get('country', account_default_country)
        account.locale = kwargs.get('locale', account_default_locale)
        account.tz = kwargs.get('tz', account_default_tz_name)
        if account.secret:
            account.secret.tel = kwargs.get('tel', None)
            account.secret.address = kwargs.get('address', None)

        self.save(account)

        def do_after_commit():
            redis_cache.delete_memoized(accountService.account_by_account_id, account.id)
            redis_cache.get_set('account_emails').remove(origin_account_email)
            redis_cache.get_set('account_emails').add(account.email)

        after_commit(do_after_commit)
        return account

    def delete_account(self, account_id):
        account = self.get_or_404(account_id)
        Account.query.filter(Account.id == account_id).delete(synchronize_session=False)

        def do_after_commit():
            redis_cache.delete_memoized(accountService.account_by_account_id, account_id)
            redis_cache.get_set('account_emails').remove(account.email)

        after_commit(do_after_commit)

    def paginate(self, account_type=None, account_email=None, account_country=None, orderby=[], offset=0, limit=10):
        filters = []
        if account_type:
            filters.append(Account.type == account_type)

        if account_email:
            filters.append(Account.email.like('%' + account_email + '%'))

        if account_country:
            filters.append(Account.country == account_country)

        order_by = []
        if not orderby:
            order_by.append(Account.id.asc())
        else:
            order_by.extend(orderby)

        count, account_ids = self.paginate_id_by(filters, orders=order_by, offset=offset, limit=limit)
        if account_ids:
            accounts = Account.query.options(sa_joinedload("secret")).filter(Account.id.in_(account_ids)).order_by(*order_by).all()
        else:
            accounts = []
        return count, accounts


    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


accountService = AccountService()