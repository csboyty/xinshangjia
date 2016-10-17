# coding:utf-8


from flask import Blueprint, render_template, request, jsonify, json
from flask_user import roles_required, current_user

bp = Blueprint("me_admin", __name__, url_prefix="/me/admin")

@bp.route("/", methods=["GET", "POST"])
@roles_required("admin")
def home():
    user = current_user._get_current_object()
    return render_template("admin/index.html", user=user)
