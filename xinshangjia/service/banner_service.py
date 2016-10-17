# coding:utf-8

from ..core import BaseService, redis_cache, after_commit
from ..model import Banner, banner_status_enable


class BannerService(BaseService):
    __model__ = Banner

    @redis_cache.memoize()
    def get_status_enabled(self, locale):
        enabled_banners = Banner.query.filter(Banner.status == banner_status_enable, Banner.locale == locale).\
            order_by(Banner.ordering.asc(), Banner.id.desc()).all()
        return [banner.as_dict() for banner in enabled_banners]

    def create_banner(self, **kwargs):
        banner = Banner()
        banner.caption = kwargs['caption']
        banner.image_url = kwargs['image_url']
        banner.link_url = kwargs.get('link_url', None)
        banner.ordering = kwargs['ordering']
        banner.status = kwargs['status']
        banner.locale = kwargs['locale']
        self.save(banner)

        def do_after_commit():
            redis_cache.delete_memoized(bannerService.get_status_enabled)

        after_commit(do_after_commit)
        return banner

    def update_banner(self, banner_id, **kwargs):
        banner = self.get_or_404(banner_id)
        banner.caption = kwargs['caption']
        banner.image_url = kwargs['image_url']
        banner.link_url = kwargs.get('link_url', None)
        banner.ordering = kwargs['ordering']
        banner.status = kwargs['status']
        banner.locale = kwargs['locale']
        self.save(banner)

        def do_after_commit():
            redis_cache.delete_memoized(bannerService.get_status_enabled)

        after_commit(do_after_commit)
        return banner

    def delete_banner(self, banner_id):
        banner = self.get_or_404(banner_id)
        self.delete(banner)

        def do_after_commit():
            redis_cache.delete_memoized(bannerService.get_status_enabled)

        after_commit(do_after_commit)
        return banner

    def paginate_banner(self, banner_caption=None, orders=[Banner.id.desc()], offset=0, limit=10):
        filters = []
        if banner_caption:
            filters.append(Banner.caption.like('%' + banner_caption + '%'))

        return self.paginate_by(filters, orders=orders, offset=offset, limit=limit)

    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


bannerService = BannerService()