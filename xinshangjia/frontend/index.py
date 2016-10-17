# coding:utf-8

from flask import Blueprint, render_template, redirect, url_for
from flask_user import login_required, current_user
from ..model import user_role_admin
from .. import qinius
from ..flask_helper import json_response

from ..core import get_locale
from ..service import artifactService, bannerService
from ..settings import artifact_per_page
from ..result_helper import multi_artifact_result

bp = Blueprint("app", __name__)


@bp.route("/", methods=["GET"])
def index():
    locale = get_locale()

    count, artifact_ids = artifactService.paginate_id(locale=locale, offset=0, limit=artifact_per_page)

    if artifact_ids:
        artifacts = multi_artifact_result(artifact_ids, locale, with_account=True, with_asset=True, with_material=True)
    else:
        artifacts = []
    banners = bannerService.get_status_enabled(locale)
    return render_template("frontend/index.html", count=count, artifacts=artifacts, banners=banners)


@bp.route("/user-home", methods=["GET"])
@login_required
def user():
    user_role = current_user._get_current_object().role
    if user_role == user_role_admin:
        return redirect(url_for("me_admin.home", _external=True))
    else:
        return redirect(url_for("artifact.home", page=1, _external=True))


@bp.route("/403", methods=["GET"])
@login_required
def unauthorized_page():
    return render_template("error/403.html"), 403


@bp.route("/qiniu-uptoken", methods=["GET"])
@login_required
def get_upload_token():
    up_token = qinius.upload_token()
    return json_response(uptoken=up_token)