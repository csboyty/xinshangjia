# coding:utf-8

from .service import accountService, artifactService, materialService


def artifact_result(artifact_id, locale, with_account=True, with_asset=True, with_material=True):
    artifact = artifactService.artifact_locale_by_artifact_id(artifact_id, locale)
    if artifact:
        if with_account and "account_id" in artifact:
            artifact['account'] = accountService.account_by_account_id(artifact['account_id'])
        if with_asset:
            artifact['assets'] = artifactService.artifact_assets_by_artifact_id(artifact_id)
        if with_material and "material_ids" in artifact:
            materials = [materialService.material_locale_by_material_id(material_id, locale) for material_id in artifact['material_ids']]
            artifact['material'] = [material for material in materials if material is not None]
    return artifact


def multi_artifact_result(artifact_ids, locale, with_account=True, with_asset=True, with_material=True):
    return [artifact_result(artifact_id, locale, with_account, with_asset, with_material) for artifact_id in artifact_ids]
