# coding:utf-8

from flask import Blueprint
from ..service import accountService, artifactService
from ..model import Artifact, account_type_designer, Account
from ..result_helper import multi_artifact_result, artifact_result
from ..flask_helper import json_response, crossdomain


bp = Blueprint('interface', __name__, url_prefix='/interface')


@bp.route("/designers/<int:designer_id>", methods=['GET', 'POST'])
@crossdomain(origin="*")
def designer_by_id(designer_id):
    designer = accountService.account_by_account_id(designer_id)
    return json_response(designer=designer)


@bp.route("/designers/page/<int:page>/size/<int:page_size>", methods=['GET', 'POST'])
@crossdomain(origin="*")
def designer_by_page(page=1, page_size=10):
    offset = (page - 1) * page_size
    limit = page_size
    count, designers = accountService.paginate(account_type=account_type_designer, orderby=[Account.id.desc()], offset=offset, limit=limit)
    return json_response(count=count, designers=designers)


@bp.route("/designers/<int:designer_id>/artifact/page/<int:page>/size/<int:page_size>/<locale>",
          methods=['GET', 'POST'])
@crossdomain(origin="*")
def designer_artifacts(designer_id, page=1, page_size=10, locale=None):
    offset = (page - 1) * page_size
    limit = page_size
    count, artifact_ids = artifactService.paginate_id(account_id=designer_id, locale=locale,
                                                      orderby=[Artifact.created.desc()], offset=offset, limit=limit)
    if artifact_ids:
        artifacts = multi_artifact_result(artifact_ids, locale, with_account=False, with_asset=True,
                                          with_material=False)
    else:
        artifacts = []

    return json_response(count=count, artifacts=artifacts)


@bp.route("/artifacts/<int:artifact_id>/<locale>", methods=['GET', 'POST'])
@crossdomain(origin="*")
def artifact_by_id(artifact_id, locale):
    artifact = artifact_result(artifact_id, locale=locale, with_account=True, with_material=True, with_asset=True)
    return json_response(artifact=artifact)

