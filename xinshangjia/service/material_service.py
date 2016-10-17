# coding:utf-8

from flask import abort
from sqlalchemy.orm import joinedload as sa_joinedload
from sqlalchemy.orm import subqueryload as sa_subqueryload
from ..core import BaseService, redis_cache, db, after_commit
from ..model import Material, MaterialTranslation


class MaterialService(BaseService):
    __model__ = Material

    @redis_cache.memoize()
    def material_locale_by_material_id(self, material_id, locale):
        materials = Material.by_locale(locale, material_id)
        return materials[0].as_dict() if materials else None

    @redis_cache.memoize()
    def material_locale_all(self, locale):
        materials = Material.by_locale(locale)
        return [material.as_dict() for material in materials]

    def create_material(self, locale, name, description):
        material = Material()
        translation = MaterialTranslation(name=name, description=description, locale=locale, fallback=True)
        material.translations.append(translation)
        self.save(material)
        material._current = translation

        def do_after_commit():
            keys = [
                materialService.material_locale_by_material_id.make_cache_key(
                    materialService.material_locale_by_material_id.uncached, material.id, material.fallback.locale),
                materialService.material_locale_all.make_cache_key(materialService.material_locale_all.uncached,
                                                                   material.fallback.locale)
            ]
            redis_cache.delete_many(*keys)

        after_commit(do_after_commit)
        return material

    def update_material(self, material_id, name, description):
        material = Material.with_fallback(material_id)
        if material:
            if material.fallback.name != name or material.fallback.description != description:
                material.fallback.name = name
                material.fallback.description = description
                Material.query.filter(MaterialTranslation.material_id == material_id, not MaterialTranslation.fallback). \
                    update({MaterialTranslation.stale: True}, synchronize_session=False)
                self.save(material.fallback)

                def do_after_commit():
                    keys = [
                        materialService.material_locale_by_material_id.make_cache_key(
                            materialService.material_locale_by_material_id.uncached, material_id,
                            material.fallback.locale),
                        materialService.material_locale_all.make_cache_key(materialService.material_locale_all.uncached,
                                                                           material.fallback.locale)
                    ]
                    redis_cache.delete_many(*keys)

                after_commit(do_after_commit)

            return material
        else:
            abort(404)

    def append_material_translation(self, material_id, locale, name, description):
        material = self.get_or_404(material_id)
        translation = MaterialTranslation(name=name, description=description, locale=locale, fallback=False)
        material.translations.append(translation)
        self.save(material)
        material._current = translation

        def do_after_commit():
            redis_cache.delete_memoized(materialService.material_locale_by_material_id, material_id, locale)

        after_commit(do_after_commit)
        return material

    def remove_material_translation(self, material_id, locale):
        translation = MaterialTranslation.query.filter(MaterialTranslation.material_id == material_id,
                                                       MaterialTranslation.locale == locale).first()
        if translation is not None:
            db.session.delete(translation)

            def do_after_commit():
                keys = [
                    materialService.material_locale_by_material_id.make_cache_key(
                        materialService.material_locale_by_material_id.uncached, material_id, locale),
                    materialService.material_locale_all.make_cache_key(materialService.material_locale_all.uncached,
                                                                       locale)
                ]
                redis_cache.delete_many(*keys)

            after_commit(do_after_commit)
        else:
            abort(404)

    def delete_material(self, material_id):
        translation_locales = Material.translation_locales(material_id)
        MaterialTranslation.query.filter(MaterialTranslation.material_id == material_id).delete(synchronize_session=False)
        Material.query.filter(Material.id == material_id).delete(synchronize_session=False)

        def do_after_commit():
            keys = [

                (
                    materialService.material_locale_by_material_id.make_cache_key(
                        materialService.material_locale_by_material_id.uncached, material_id, locale),
                    materialService.material_locale_all.make_cache_key(materialService.material_locale_all.uncached,
                                                                       locale)
                )
                for locale in translation_locales
            ]
            redis_cache.delete_many(*[key for sub_keys in keys for key in sub_keys])

        after_commit(do_after_commit)

    def paginate_with_translations(self, material_name=None, offset=0, limit=10):
        filters = [MaterialTranslation.fallback]
        if material_name:
            filters.append(MaterialTranslation.name.like("%" + material_name + "%"))

        material_query = MaterialTranslation.query.filter(*filters)

        count = material_query.with_entities(db.func.count(MaterialTranslation.material_id)).scalar()
        if count:
            material_ids = material_query.with_entities(MaterialTranslation.material_id)\
                .order_by(MaterialTranslation.material_id.desc()).offset(offset).limit(limit).all()
            material_ids = [id_ for (id_, ) in material_ids]
            materials = Material.query.options(sa_subqueryload("translations")).\
                filter(Material.id.in_(material_ids)).all()
        else:
            materials = []
        return count, materials

    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


materialService = MaterialService()




