# coding:utf-8

from flask import abort
from sqlalchemy.orm import joinedload as sa_joinedload
from sqlalchemy.orm import subqueryload as sa_subqueryload
from ..core import BaseService, redis_cache, db, after_commit
from ..model import Artifact, ArtifactMaterial, ArtifactAsset, ArtifactTranslation, MaterialTranslation
from ..tasks import gen_qiniu_thumbnail, remove_qiniu_thumbnail, remove_qiniu_key
from ..settings import artifact_thumbnails, asset_thumbnails


class ArtifactService(BaseService):
    __model__ = Artifact

    @redis_cache.memoize()
    def artifact_locale_by_artifact_id(self, artifact_id, locale):
        artifacts = Artifact.by_locale(locale, artifact_id)
        return artifacts[0].as_dict() if artifacts else None

    @redis_cache.memoize()
    def artifact_assets_by_artifact_id(self, artifact_id):
        assets = ArtifactAsset.query.filter(ArtifactAsset.artifact_id == artifact_id).order_by(ArtifactAsset.id).all()
        return [asset.as_dict() for asset in assets]

    def create_artifact(self, locale, **kwargs):
        artifact = Artifact()
        artifact.preview_image = kwargs['preview_image']
        artifact._artifact_materials = [ArtifactMaterial(material_id=int(material_id)) for material_id in
                                        kwargs['material_ids']]
        artifact.assets = [
            ArtifactAsset(media_file=asset_dict['media_file'], media_filename=asset_dict['media_filename']) for
            asset_dict in kwargs['assets']]
        artifact.account_id = kwargs['account_id']
        artifact.reference = kwargs.get('reference')

        translation = ArtifactTranslation(locale=locale, name=kwargs['name'], abstract=kwargs['abstract'],
                                          fallback=True)
        artifact.translations.append(translation)

        ArtifactService.handle_preview_image(None, artifact.preview_image)
        ArtifactService.handle_assets([], artifact.assets)
        self.save(artifact)
        artifact._current = translation

        def do_after_commit():
            redis_cache.delete_memoized(artifactService.artifact_locale_by_artifact_id, artifact.id, locale)

        after_commit(do_after_commit)

        return artifact

    def append_artifact_translation(self, artifact_id, locale, **kwargs):
        artifact = self.get_or_404(artifact_id)
        translation = ArtifactTranslation(locale=locale, name=kwargs['name'], abstract=kwargs['abstract'],
                                          fallback=False)
        artifact.translations.append(translation)
        self.save(artifact)
        artifact._current = translation

        def do_after_commit():
            redis_cache.delete_memoized(artifactService.artifact_locale_by_artifact_id, artifact_id, locale)

        after_commit(do_after_commit)
        return artifact

    def remove_artifact_translation(self, artifact_id, locale):
        translation = ArtifactTranslation.query.filter(ArtifactTranslation.artifact_id == artifact_id,
                                                       ArtifactTranslation.locale == locale).first()
        if translation is not None:
            db.session.delete(translation)

            def do_after_commit():
                redis_cache.delete_memoized(artifactService.artifact_locale_by_artifact_id, artifact_id, locale)

            after_commit(do_after_commit)
        else:
            abort(404)

    def update_artifact(self, artifact_id, **kwargs):
        artifact = Artifact.query.options(sa_joinedload("fallback"), sa_joinedload("assets")).filter(
            Artifact.id == artifact_id).first()
        if artifact:
            stale = False
            if artifact.fallback.name != kwargs['name'] or artifact.fallback.abstract != kwargs['abstract']:
                stale = True

            artifact.fallback.name = kwargs['name']
            artifact.fallback.abstract = kwargs['abstract']

            artifact._artifact_materials = [ArtifactMaterial(artifact_id=artifact_id, material_id=int(material_id))
                                            for material_id in kwargs['material_ids']]
            new_preview_image = kwargs['preview_image']
            new_assets = [
                ArtifactAsset(artifact_id=artifact_id, media_file=asset_dict['media_file'],
                              media_filename=asset_dict['media_filename'])
                for asset_dict in kwargs['assets']]
            artifact.account_id = kwargs['account_id']
            artifact.reference = kwargs.get('reference')

            ArtifactService.handle_preview_image(artifact.preview_image, new_preview_image)
            ArtifactService.handle_assets(artifact.assets, new_assets)
            artifact.preview_image = new_preview_image

            if stale:
                ArtifactTranslation.query.filter(ArtifactTranslation.artifact_id == artifact_id, not ArtifactTranslation.fallback). \
                    update({ArtifactTranslation.stale: True}, synchronize_session=False)
            self.save(artifact)

            def do_after_commit():
                keys = [
                    artifactService.artifact_locale_by_artifact_id. \
                        make_cache_key(artifactService.artifact_locale_by_artifact_id.uncached, artifact_id,
                                       artifact.locale),
                    artifactService.artifact_assets_by_artifact_id. \
                        make_cache_key(artifactService.artifact_assets_by_artifact_id.uncached, artifact_id)
                ]
                redis_cache.delete_many(*keys)

            after_commit(do_after_commit)
            return artifact
        else:
            abort(404)

    def delete_artifact(self, artifact_id):
        artifact = self.get_or_404(artifact_id)
        translation_locales = Artifact.translation_locales(artifact_id)
        ArtifactService.handle_preview_image(artifact.preview_image, None)
        ArtifactService.handle_assets(artifact.assets, [])
        ArtifactTranslation.query.filter(ArtifactTranslation.artifact_id == artifact_id). \
            delete(synchronize_session=False)
        Artifact.query.filter(Artifact.id == artifact_id).delete(synchronize_session=False)

        def do_after_commit():
            keys = [
                artifactService.artifact_locale_by_artifact_id. \
                    make_cache_key(artifactService.artifact_locale_by_artifact_id.uncached, artifact_id, locale)
                for locale in translation_locales
            ]
            keys.append(artifactService.artifact_assets_by_artifact_id.
                        make_cache_key(artifactService.artifact_assets_by_artifact_id.uncached, artifact_id))
            redis_cache.delete_many(*keys)

        after_commit(do_after_commit)

    @classmethod
    def handle_preview_image(cls, old_preview_image, new_preivew_image):
        def do_handle_preview_image():
            if old_preview_image != new_preivew_image:
                if old_preview_image is not None:
                    remove_qiniu_thumbnail.delay(old_preview_image, artifact_thumbnails)
                    remove_qiniu_key.delay(old_preview_image)

                gen_qiniu_thumbnail.delay(new_preivew_image, artifact_thumbnails)

        after_commit(do_handle_preview_image)


    @classmethod
    def handle_assets(cls, old_assets, new_assets):
        old_asset_set = set(old_assets)
        new_asset_set = set(new_assets)
        append_asset_set = new_asset_set - old_asset_set
        remove_asset_set = old_asset_set - new_asset_set

        for asset in remove_asset_set:
            old_assets.remove(asset)

        for asset in append_asset_set:
            old_assets.append(asset)

        def do_handle_assets():
            for asset in append_asset_set:
                gen_qiniu_thumbnail.delay(asset.media_file, asset_thumbnails)

            for asset in remove_asset_set:
                remove_qiniu_thumbnail.delay(asset.media_file, asset_thumbnails)
                remove_qiniu_key.delay(asset.media_file)

        after_commit(do_handle_assets)


    def paginate_id(self, artifact_name=None, material_name=None, account_id=None, locale=None, orderby=[], offset=0,
                    limit=10):
        filters = []
        artifact_query = Artifact.query

        if artifact_name:
            filters.append(ArtifactTranslation.name.like('%' + artifact_name + '%'))

        if locale:
            artifact_query = artifact_query.join(ArtifactTranslation, \
                 db.and_(ArtifactTranslation.artifact_id == Artifact.id, ArtifactTranslation.locale == locale))
        else:
            artifact_query = artifact_query.join(ArtifactTranslation, \
                  db.and_(ArtifactTranslation.artifact_id == Artifact.id, ArtifactTranslation.fallback))

        if material_name:
            artifact_query = artifact_query. \
                join(ArtifactMaterial, ArtifactTranslation.artifact_id == ArtifactMaterial.artifact_id).\
                join(MaterialTranslation,
                     db.and_(MaterialTranslation.material_id == ArtifactMaterial.material_id,
                             MaterialTranslation.name == material_name))

        if account_id:
            filters.append(Artifact.account_id == account_id)

        order_by = []
        if not orderby:
            order_by.append(ArtifactTranslation.artifact_id.desc())
        else:
            order_by.extend(orderby)

        count = artifact_query.with_entities(db.func.count(Artifact.id)).filter(*filters).scalar()
        if count:
            artifact_ids = artifact_query.with_entities(Artifact.id).filter(*filters)\
                .order_by(*order_by).offset(offset).limit(limit).all()
            artifact_ids = [id_ for (id_,) in artifact_ids]
        else:
            artifact_ids = []
        return count, artifact_ids

    def paginate_with_translations(self, artifact_name=None, material_name=None, offset=0, limit=10):
        filters = [ArtifactTranslation.fallback]

        artifact_query = ArtifactTranslation.query

        if artifact_name:
            filters.append(ArtifactTranslation.name.like('%' + artifact_name + '%'))

        if material_name:
            artifact_query = artifact_query. \
                join(ArtifactMaterial, ArtifactTranslation.artifact_id == ArtifactMaterial.artifact_id).\
                join(MaterialTranslation,
                     db.and_(MaterialTranslation.material_id == ArtifactMaterial.material_id,
                             MaterialTranslation.name == material_name))

        count = artifact_query.with_entities(db.func.count(ArtifactTranslation.artifact_id)).filter(*filters).scalar()
        if count:
            artifact_ids = artifact_query.with_entities(ArtifactTranslation.artifact_id).filter(*filters).\
                order_by(ArtifactTranslation.artifact_id.desc()).offset(offset).limit(limit).all()
            artifact_ids = [id_ for (id_,) in artifact_ids]
            artifacts = Artifact.query.options(sa_subqueryload("translations"), sa_subqueryload("account"),
                                               sa_subqueryload("_artifact_materials")). \
                filter(Artifact.id.in_(artifact_ids)).order_by(Artifact.id.desc()).all()
        else:
            artifacts = []
        return count, artifacts

    def __repr__(self):
        return "{0}.{1}".format(self.__model__, self.__class__.__name__)


artifactService = ArtifactService()








