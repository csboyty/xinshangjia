# coding:utf-8

import sqlalchemy as sa
from sqlalchemy.orm import joinedload as sa_joinedload
from ..core import db
from ..sqlalchemy_helper import TimestampMixin, AsDictMixin, Deleted


class ArtifactTag(db.Model):
    __tablename__ = "artifact_tag"

    artifact_id = db.Column(db.Integer(), db.ForeignKey('artifact.id', ondelete='cascade'), primary_key=True)
    tag_id = db.Column(db.Integer(), db.ForeignKey('tag.id', ondelete='cascade'), primary_key=True)


class ArtifactMaterial(db.Model):
    __tablename__ = "artifact_material"

    artifact_id = db.Column(db.Integer(), db.ForeignKey('artifact.id', ondelete='cascade'), primary_key=True)
    material_id = db.Column(db.Integer(), db.ForeignKey('material.id', ondelete='cascade'), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, ArtifactMaterial) and self.artifact_id == other.artifact_id \
                and self.material_id == other.material_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return (self.artifact_id if self.artifact_id else 0) + self.material_id*13


class Artifact(db.Model, TimestampMixin, AsDictMixin, Deleted):
    __tablename__ = 'artifact'
    __dictfields__ = dict(include=['id', "material_ids", "account_id", "reference", "preview_image",
                                   'name', 'abstract', "locale"])

    id = db.Column(db.Integer(), primary_key=True)
    _artifact_materials = db.relationship("ArtifactMaterial", passive_deletes=True, cascade="all,delete-orphan")
    preview_image = db.Column(db.String(256), nullable=False)
    assets = db.relationship("ArtifactAsset", passive_deletes=True, cascade="all,delete-orphan")

    reference = db.Column(db.String(256), nullable=True)
    account_id = db.Column(db.Integer(), db.ForeignKey("account.id", ondelete="cascade"), nullable=False)
    account = db.relationship("Account", uselist=False, backref="artifacts")
    translations = db.relationship("ArtifactTranslation", order_by="desc(ArtifactTranslation.fallback)", passive_deletes=True, cascade="all,delete-orphan")
    fallback = db.relationship("ArtifactTranslation",
                               primaryjoin="and_(Artifact.id==ArtifactTranslation.artifact_id, ArtifactTranslation.fallback)", uselist=False)

    _current = None

    @property
    def material_ids(self):
        return [_artifact_material.material_id for _artifact_material in self._artifact_materials]

    @property
    def name(self):
        if self._current is not None:
            return self._current.name
        else:
            return None


    @property
    def abstract(self):
        if self._current is not None:
            return self._current.abstract
        else:
            return None

    @property
    def locale(self):
        if self._current is not None:
            return self._current.locale
        else:
            return None

    @classmethod
    def by_locale(cls, locale, *artifact_id):
        filters = []
        if artifact_id:
            filters.append(Artifact.id.in_(artifact_id))

        artifacts_with_translation = db.session.query(Artifact, ArtifactTranslation). \
            outerjoin(ArtifactTranslation, sa.and_(Artifact.id == ArtifactTranslation.artifact_id, ArtifactTranslation.locale == locale)). \
            filter(*filters).order_by(Artifact.id.asc()).all()

        artifacts = []
        for artifact, translation in artifacts_with_translation:
            if translation is not None:
                artifact._current = translation
                artifacts.append(artifact)

        return artifacts

    @classmethod
    def with_fallback(cls, *artifact_id):
        filters = []
        if artifact_id:
            filters.append(Artifact.id.in_(artifact_id))

        artifacts_with_fallback = Artifact.query.options(sa_joinedload("fallback"), sa_joinedload("assets")).filter(*filters).order_by(Artifact.id.asc()).all()
        for artifact in artifacts_with_fallback:
            artifact._current = artifact.fallback
        return artifacts_with_fallback

    @classmethod
    def translation_locales(cls, artifact_id):
        return [locale for (locale,) in
                ArtifactTranslation.query.with_entities(ArtifactTranslation.locale).filter(ArtifactTranslation.artifact_id == artifact_id).all()]

    def __eq__(self, other):
        if isinstance(other, Artifact) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)


class ArtifactTranslation(db.Model):
    __tablename__ = "artifact_translation"
    __table_args__ = (db.PrimaryKeyConstraint('artifact_id', 'locale', name='artifact_translation_pk'),)

    artifact_id = db.Column(db.Integer(), db.ForeignKey("artifact.id", ondelete='CASCADE'), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    name = db.Column(db.Unicode(32), nullable=False)
    abstract = db.Column(db.Text(), nullable=False)
    fallback = db.Column(db.Boolean(), nullable=False, default=False)
    stale = db.Column(db.Boolean(), nullable=False, default=False)

    def __eq__(self, other):
        if isinstance(other, ArtifactTranslation) and self.artifact_id == other.artifact_id and self.locale == other.locale:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.artifact_id) * 13 + hash(self.locale) * 17

    def __repr__(self):
        return "{0}.{1}({2}-{3})".format(self.__module__, self.__class__.__name__, self.artifact_id, self.lang)


class ArtifactAsset(db.Model, TimestampMixin, AsDictMixin):
    __tablename__ = "artifact_asset"
    __dictfields__ = dict(include=["id", "media_file", "media_filename"])

    id = db.Column(db.Integer(), primary_key=True)
    artifact_id = db.Column(db.Integer(), db.ForeignKey("artifact.id", ondelete="cascade"), nullable=False)
    media_file = db.Column(db.Unicode(256), nullable=False)
    media_filename = db.Column(db.Unicode(64), nullable=False)

    def __eq__(self, other):
        if isinstance(other, ArtifactAsset) and self.media_file == other.media_file:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.media_file)

    def __repr__(self):
        return "{0}.{1}({2})".format(self.__module__, self.__class__.__name__, self.id)




