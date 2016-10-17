# coding:utf-8

from flask import Blueprint, render_template, request, json
from flask_user import current_user, roles_required
from ..core import get_locale
from ..service import artifactService
from ..model import Material, Artifact, Account
from ..flask_helper import json_response
from ..sqlalchemy_helper import asdict

bp = Blueprint("artifact_admin", __name__, url_prefix="/me/admin/artifact")


@bp.route("/", methods=["GET", "POST"])
@roles_required("admin")
def home():
    user = current_user._get_current_object()
    return render_template("admin/worksMgr.html", user=user)


@bp.route('/create-artifact', methods=["GET"])
@bp.route('/update-artifact/<int:artifact_id>', methods=["GET"])
@roles_required("admin")
def create_artifact_page(artifact_id=None):
    user = current_user._get_current_object()
    materials = Material.with_fallback()
    designers = Account.query.order_by(Account.first_name.asc()).all()
    if artifact_id:
        artifact = Artifact.with_fallback(artifact_id)[0]
    else:
        artifact = {}
    return render_template("admin/workUpdate.html", user=user, materials=materials, designers=designers,
                           artifact=artifact)


@bp.route('/save-artifact', methods=["POST"])
@roles_required("admin")
def save_artifact():
    artifact_data = json.loads(request.form.get('data'))
    artifact_id = artifact_data.pop('id', None)

    if artifact_id:
        artifact = artifactService.update_artifact(int(artifact_id), **artifact_data)
    else:
        locale = artifact_data.pop('locale', get_locale())
        artifact = artifactService.create_artifact(locale, **artifact_data)

    return json_response(artifact=artifact)


@bp.route('/delete-artifact/<int:artifact_id>', methods=["POST"])
@roles_required("admin")
def delete_artifact(artifact_id):
    artifactService.delete_artifact(artifact_id)
    return json_response()


@bp.route("/<int:artifact_id>/translation-exist", methods=["GET"])
def artifact_translation_exists(artifact_id):
    locale = request.args.get("locale")
    locales = Artifact.translation_locales(artifact_id)
    unique = not (locale in locales)
    return json_response(unique=unique)


@bp.route('/<int:artifact_id>/append-translation', methods=["GET"])
@roles_required("admin")
def append_artifact_translation_page(artifact_id):
    artifact = Artifact.with_fallback(artifact_id)[0]
    return json_response(artifact=artifact)


@bp.route('/<int:artifact_id>/append-translation', methods=["POST"])
@roles_required("admin")
def append_artifact_translatioin(artifact_id):
    artifact_translation_data = json.loads(request.form.get("data"))
    locale = artifact_translation_data.pop('locale')
    artifact = artifactService.append_artifact_translation(artifact_id, locale, **artifact_translation_data)
    return json_response(artifact=artifact)


@bp.route('/<int:artifact_id>/remove-translation', methods=["POST"])
@roles_required("admin")
def remove_artifact_translation(artifact_id):
    locale = request.form.get("locale")
    artifactService.remove_artifact_translation(artifact_id, locale)
    return json_response()


@bp.route('/<int:artifact_id>/assets', methods=["GET"])
@roles_required("admin")
def artifact_assets(artifact_id):
    assets = artifactService.artifact_assets_by_artifact_id(artifact_id)
    return json_response(assets=assets)


@bp.route('/list', methods=['GET'])
@roles_required("admin")
def list_artifact():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    artifact_name = request.args.get("artifact_name", None)
    material_name = request.args.get("material_name", None)
    count, artifacts = artifactService.paginate_with_translations(artifact_name=artifact_name,
                                                                  material_name=material_name, offset=offset,
                                                                  limit=limit)
    artifact_dicts = []
    if artifacts:
        material_id_name_dict = dict([(material.id, material.name) for material in Material.with_fallback()])
        for artifact in artifacts:
            artifact_dict = dict(id=artifact.id, preview_image=artifact.preview_image, reference=artifact.reference)
            artifact_stale = False
            artifact_translations = []
            for translation in artifact.translations:
                artifact_translations.append(asdict(translation, include=["locale", "name", "abstract", "stale"]))
                if translation.stale:
                    artifact_stale = True

            artifact_dict['translations'] = artifact_translations
            artifact_dict['account'] = asdict(artifact.account, **Account.__dictfields__)
            artifact_dict['materials'] = [material_id_name_dict.get(material_id) for material_id in artifact.material_ids]
            artifact_dict['stale'] = artifact_stale
            artifact_dicts.append(artifact_dict)

    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=artifact_dicts)


