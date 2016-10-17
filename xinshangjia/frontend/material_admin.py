# coding:utf-8

from flask import Blueprint, render_template, request, json
from flask_user import current_user, roles_required
from ..core import get_locale
from ..service import materialService
from ..model import Material,MaterialTranslation
from ..flask_helper import json_response
from ..sqlalchemy_helper import asdict

bp = Blueprint("material_admin", __name__, url_prefix="/me/admin/material")


@bp.route("/", methods=["GET", "POST"])
@roles_required("admin")
def home():
    user = current_user._get_current_object()
    return render_template("admin/categoryMgr.html", user=user)


@bp.route("/material-exist", methods=["GET"])
def material_exists():
    name = request.args.get("name")
    unique = not (MaterialTranslation.translation_name_exist(name))
    return json_response(unique=unique)


@bp.route('/create-material', methods=["POST"])
@roles_required("admin")
def create_material():
    material_data = json.loads(request.form.get('data'))
    locale = material_data.get('locale', get_locale())
    name = material_data.get('name')
    description = material_data.get('description', '')
    material = materialService.create_material(locale, name, description)
    return json_response(material=material)


@bp.route('/update-material/<int:material_id>', methods=["POST"])
@roles_required("admin")
def update_material(material_id):
    material_data = json.loads(request.form.get('data'))
    name = material_data.get('name')
    description = material_data.get('description', '')
    material = materialService.update_material(material_id, name, description)
    return json_response(material=material)


@bp.route('/delete-material/<int:material_id>', methods=["POST"])
@roles_required("admin")
def delete_artifact(material_id):
    materialService.delete_material(material_id)
    return json_response()


@bp.route("/<int:material_id>/translation-exist", methods=["GET"])
def material_translation_exists(material_id):
    locale = request.args.get("locale")
    locales = Material.translation_locales(material_id)
    unique = not (locale in locales)
    return json_response(unique=unique)


@bp.route('/<int:material_id>/append-translation', methods=["POST"])
@roles_required("admin")
def append_material_translation(material_id):
    material_translation_data = json.loads(request.form.get("data"))
    locale = material_translation_data.get('locale')
    name = material_translation_data.get('name')
    description = material_translation_data.get('description', '')
    material = materialService.append_material_translation(material_id, locale, name, description)
    return json_response(material=material)


@bp.route('/<int:material_id>/remove-translation', methods=["POST"])
@roles_required("admin")
def remove_material_translation(material_id):
    locale = request.form.get("locale")
    materialService.remove_material_translation(material_id, locale)
    return json_response()


@bp.route('/list', methods=['GET'])
@roles_required("admin")
def list_material():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    material_name = request.args.get("material_name", None)
    count, materials = materialService.paginate_with_translations(material_name=material_name, offset=offset,
                                                                  limit=limit)
    material_dicts = []
    if materials:
        for material in materials:
            material_dict = dict(id=material.id)
            material_translations = []
            material_stale = False
            for translation in material.translations:
                material_translations.append(asdict(translation, include=["locale", "name", "stale"]))
                if translation.stale:
                    material_stale = True

            material_dict['translations'] = material_translations
            material_dict['stale'] = material_stale
            material_dicts.append(material_dict)

    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=material_dicts)




