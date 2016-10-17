# coding:utf-8

from flask import Blueprint, render_template
from ..settings import designer_per_page, designer_artifact_per_page
from ..service import accountService, materialService, artifactService
from ..model import account_type_designer, Artifact, Account
from ..core import get_locale
from ..result_helper import multi_artifact_result

bp = Blueprint("designer", __name__, url_prefix="/designer")


@bp.route("/", methods=["GET", "POST"])
@bp.route("/page/<int:page>/", methods=["GET", "POST"])
def home(page=1):
    offset = (page - 1) * designer_per_page
    limit = designer_per_page
    count, designers = accountService.paginate(account_type=account_type_designer, offset=offset, limit=limit,orderby=[Account.id.desc()])
    return render_template("frontend/designers.html", count=count, designers=designers, page=page)


@bp.route("/detail/<int:account_id>/", methods=["GET", "POST"])
@bp.route("/detail/<int:account_id>/artifact/page/<int:page>", methods=["GET", "POST"])
def show_designer(account_id, page=1):
    locale = get_locale()
    account = accountService.account_by_account_id(account_id)
    count = 0
    artifacts = []
    if account:
        offset = (page - 1) * designer_artifact_per_page
        limit = designer_artifact_per_page
        count, artifact_ids = artifactService.paginate_id(account_id=account_id, locale=locale,
                                                          orderby=[Artifact.created.desc()], offset=offset, limit=limit)

        if artifact_ids:
            artifacts = multi_artifact_result(artifact_ids, locale, with_account=False, with_asset=False,
                                              with_material=False)

    return render_template("frontend/designerDetail.html", artifact_count=count, artifacts=artifacts, designer=account,
                           page=page)
