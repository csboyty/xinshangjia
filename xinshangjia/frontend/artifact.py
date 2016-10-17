# coding:utf-8

from flask import Blueprint, render_template
from ..core import get_locale
from ..service import artifactService, bannerService, materialService
from ..settings import artifact_per_page
from ..result_helper import multi_artifact_result, artifact_result

bp = Blueprint("artifact", __name__, url_prefix="/artifact")


@bp.route("/", methods=["GET", "POST"])
@bp.route("/page/<int:page>/", methods=["GET", "POST"])
def home(page=1):
    locale = get_locale()

    offset = (page - 1) * artifact_per_page
    limit = artifact_per_page
    count, artifact_ids = artifactService.paginate_id(locale=locale, offset=offset, limit=limit)

    if artifact_ids:
        artifacts = multi_artifact_result(artifact_ids, locale, with_account=True, with_asset=True, with_material=True)
    else:
        artifacts = []
    banners = bannerService.get_status_enabled(locale)
    return render_template("frontend/index.html", count=count, artifacts=artifacts, page=page, banners=banners)


@bp.route("/material/<material_name>/", methods=["GET", "POST"])
@bp.route("/material/<material_name>/page/<int:page>/", methods=["GET", "POST"])
def artifact_by_material(material_name=None, page=1):
    locale = get_locale()
    offset = (page - 1) * artifact_per_page
    limit = artifact_per_page
    count, artifact_ids = artifactService.paginate_id(material_name=material_name, locale=locale, offset=offset,
                                                      limit=limit)
    if artifact_ids:
        artifacts = multi_artifact_result(artifact_ids, locale, with_account=True, with_asset=True, with_material=True)
    else:
        artifacts = []

    return render_template("frontend/category.html", count=count, artifacts=artifacts, page=page,
                           material=material_name)


@bp.route("/detail/<int:artifact_id>/", methods=["GET", "POST"])
def show_artifact(artifact_id):
    locale = get_locale()
    artifact = artifact_result(artifact_id, locale=locale)
    return render_template("frontend/workDetail.html", artifact=artifact)



