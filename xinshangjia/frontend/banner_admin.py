# coding:utf-8

from flask import Blueprint, render_template, request, json
from flask_user import roles_required, current_user
from ..service import bannerService
from ..model import Banner
from ..flask_helper import json_response


bp = Blueprint('banner_admin', __name__, url_prefix="/me/admin/banner")


@bp.route("/", methods=["GET", "POST"])
@roles_required("admin")
def home():
    user = current_user._get_current_object()
    return render_template("admin/slideMgr.html", user=user)


@bp.route('/create-banner', methods=["GET"])
@bp.route("/update-banner/<int:banner_id>", methods=["GET"])
@roles_required("admin")
def create_banner_page(banner_id=None):
    user = current_user._get_current_object()
    if banner_id:
        banner = bannerService.get(banner_id)
    else:
        banner = {}
    return render_template("admin/slideUpdate.html", user=user, banner=banner)


@bp.route('/save-banner', methods=["POST"])
@roles_required("admin")
def save_banner():
    banner_data = json.loads(request.form.get('data'))
    banner_id = banner_data.pop('id', None)
    if banner_id:
        banner = bannerService.update_banner(banner_id, **banner_data)
    else:
        banner = bannerService.create_banner(**banner_data)
    return json_response(banner=banner)


@bp.route("/delete-banner/<int:banner_id>", methods=["POST"])
@roles_required("admin")
def delete_banner(banner_id):
    bannerService.delete_banner(banner_id)
    return json_response()


@bp.route("/list", methods=["GET"])
@roles_required("admin")
def list_banner():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    caption = request.args.get("banner_caption", None)
    count, banners = bannerService.\
        paginate_banner(caption, orders=[Banner.status.desc(), Banner.ordering.desc(), Banner.id.desc()], limit=limit, offset=offset)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=banners)
