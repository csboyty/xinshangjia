# coding:utf-8


from ..core import BaseService, redis_cache
from ..model import Tag
from .. import utils


class TagService(BaseService):
    __model__ = Tag

    @redis_cache.memoize()
    def tag_by_id(self, tag_id):
        tag = self.get(tag_id)
        if tag:
            return utils.dotdict(tag.asdict())

    def add_tag(self, tag_name, tag_type):
        tag = Tag(name=tag_name, type=tag_type)
        self.save(tag)
        return tag

    def remove_tag(self, tag_id):
        tag = self.get_or_404(tag_id)
        self.delete(tag)

    def paginate_by(self, tag_name=None, tag_type=None, order_by=Tag.id.desc(), offset=0, limit=10):
        filters = []
        if tag_name:
            name = '%' + tag_name + '%'
            filters.append(Tag.name.like(name))
        if tag_type:
            filters.append(Tag.type == tag_type)

        count, tag = BaseService.paginate_by(self, filters=filters, orders=[order_by], offset=offset, limit=limit)
        return count, tag

    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


tagService = TagService()


def expire_tag(tag_id):
    redis_cache.delete_memoized(tagService.tag_by_id, tag_id)

