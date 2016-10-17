# coding:utf-8

import sqlalchemy as sa
from sqlalchemy.orm import joinedload as sa_joinedload
from ..core import db
from ..sqlalchemy_helper import AsDictMixin


class Material(db.Model, AsDictMixin):
    __tablename__ = "material"
    __dictfields__ = dict(include=["id", "name", "locale", "description"])

    id = db.Column(db.Integer(), primary_key=True)
    translations = db.relationship("MaterialTranslation",
                                   order_by="desc(MaterialTranslation.fallback)", passive_deletes=True,
                                   cascade="all,delete-orphan")
    fallback = db.relationship("MaterialTranslation",
                               primaryjoin="and_(Material.id==MaterialTranslation.material_id, MaterialTranslation.fallback)",
                               uselist=False)
    _current = None

    @property
    def name(self):
        if self._current is not None:
            return self._current.name
        else:
            return None

    @property
    def description(self):
        if self._current is not None:
            return self._current.description
        else:
            return None

    @property
    def locale(self):
        if self._current is not None:
            return self._current.locale
        else:
            return None

    @property
    def fallback_name(self):
        return self.fallback.name

    @property
    def current(self):
        return self._current

    @classmethod
    def by_locale(cls, locale, *material_id):
        filters = []
        if material_id:
            filters.append(Material.id.in_(material_id))

        materials_with_translation = db.session.query(Material, MaterialTranslation). \
            outerjoin(MaterialTranslation,
                      sa.and_(Material.id == MaterialTranslation.material_id, MaterialTranslation.locale == locale)). \
            filter(*filters).order_by(Material.id.asc()).all()

        materials = []
        for material, translation in materials_with_translation:
            if translation is not None:
                material._current = translation
                materials.append(material)

        return materials

    @classmethod
    def with_fallback(cls, *material_id):
        filters = []
        if material_id:
            filters.append(Material.id.in_(material_id))
        materials_with_fallback = Material.query.options(sa_joinedload("fallback")).filter(*filters).order_by(
            Material.id.asc()).all()
        for material in materials_with_fallback:
            material._current = material.fallback

        return materials_with_fallback

    @classmethod
    def by_locale_name(cls, locale, name):
        material_with_translation = db.session.query(Material, MaterialTranslation).\
            join(MaterialTranslation,
                 sa.and_(Material.id == MaterialTranslation.material_id, MaterialTranslation.locale == locale)). \
            filter(MaterialTranslation.name == name, MaterialTranslation.locale == locale).first()
        if material_with_translation:
            material, translation = material_with_translation
            material._current = translation
            return material
        else:
            return None

    @classmethod
    def translation_locales(cls, material_id):
        return [locale for (locale,) in
                MaterialTranslation.query.with_entities(MaterialTranslation.locale).filter(
                    MaterialTranslation.material_id == material_id).all()]

    def __eq__(self, other):
        if isinstance(other, Material) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)


class MaterialTranslation(db.Model):
    __tablename__ = "material_translation"
    __table_args__ = (db.PrimaryKeyConstraint('material_id', 'locale', name='material_translation_pk'),
                      db.UniqueConstraint('locale', 'name', name='material_translation_uk'))

    material_id = db.Column(db.Integer(), db.ForeignKey("material.id"), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    name = db.Column(db.Unicode(32), nullable=False)
    description = db.Column(db.Unicode(512), nullable=True)
    fallback = db.Column(db.Boolean(), nullable=False, default=False)
    stale = db.Column(db.Boolean(), nullable=False, default=False)

    @classmethod
    def translation_name_exist(cls, name):
        return MaterialTranslation.query.with_entities(db.func.count(MaterialTranslation.material_id)).\
            filter(MaterialTranslation.name == name).scalar() > 0

    def __eq__(self, other):
        if isinstance(other,
                      MaterialTranslation) and self.material_id == other.material_id and self.locale == other.locale:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.material_id) * 13 + hash(self.locale) * 17

    def __repr__(self):
        return "{0}.{1}({2}-{3})".format(self.__module__, self.__class__.__name__, self.material_id, self.locale)


