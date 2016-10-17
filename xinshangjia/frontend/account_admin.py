# coding:utf-8

from flask import Blueprint, render_template, request, jsonify, json
from flask_user import roles_required, current_user
from ..core import redis_cache
from ..service import accountService
from ..model import account_type_designer
from ..flask_helper import json_response
from ..sqlalchemy_helper import asdict


bp = Blueprint('account_admin', __name__, url_prefix="/me/admin/account")


@bp.route("/designer", methods=["GET", "POST"])
@roles_required("admin")
def designer_mgr():
    user = current_user._get_current_object()
    return render_template("admin/designerMgr.html", user=user)


@bp.route("/email-exist", methods=["GET"])
def account_email_exists():
    email = request.args.get("email")
    unique = not (redis_cache.get_set("account_emails").sismember(email))
    return json_response(unique=unique)


@bp.route('/create-designer', methods=["GET"])
@bp.route('/update-designer/<int:account_id>', methods=["GET"])
@roles_required("admin")
def create_or_udpate_designer_page(account_id=None):
    if account_id:
        designer_account = accountService.get(account_id)
    else:
        designer_account = {}
    user = current_user._get_current_object()
    return render_template("admin/designerUpdate.html", user=user, designer=designer_account)


@bp.route('/save-designer', methods=["POST"])
@roles_required("admin")
def save_designer():
    designer_account_data = json.loads(request.form.get('data'))
    account_id = designer_account_data.pop('id', None)
    if account_id:
        designer_account = accountService.update_account(account_id, **designer_account_data)
    else:
        designer_account = accountService.create_account(account_type_designer, **designer_account_data)
    return json_response(designer_account=designer_account)


@bp.route("/delete-designer/<int:account_id>", methods=["POST"])
@roles_required("admin")
def delete_designer(account_id):
    accountService.delete_account(account_id)
    return json_response()


@bp.route("/list", methods=["GET"])
@roles_required("admin")
def list_account():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    account_type = request.args.get('account_type', 1)
    account_email = request.args.get("account_email", None)
    account_country = request.args.get("account_country", None)
    count, accounts = accountService.paginate(account_type=account_type, account_email=account_email,
                                              account_country=account_country, limit=limit, offset=offset)
    if accounts:
        accounts = [asdict(account,
                           include=["id", "type", "email", "first_name", "last_name", "nick_name", "image_url",
                                    "country", "country_name", "tz", "secret_info"]) for account in accounts]
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=accounts)







