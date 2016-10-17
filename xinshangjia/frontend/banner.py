# coding:utf-8

from flask import Blueprint
from ..core import get_locale
from ..service import bannerService
from ..flask_helper import json_response

bp = Blueprint("banner", __name__, url_prefix="/banner")


@bp.route("/", methods=["GET", "POST"])
def home():
    locale = get_locale()
    banners = bannerService.get_status_enabled(locale)
    return json_response(banners=banners)