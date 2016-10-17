# coding:utf-8


from werkzeug.local import LocalProxy
from flask import current_app, request, jsonify, render_template, send_file
from sqlalchemy.exc import DataError

from ..core import AppError, get_locale
from ..logs import init_app_logger

from .. import factory


_logger = LocalProxy(lambda: current_app.logger)


def create_app(settings_override=None):
    app = factory.create_app(__name__, __path__, settings_override=settings_override)
    app.errorhandler(DataError)(on_sa_data_error)
    app.errorhandler(AppError)(on_app_error)
    app.errorhandler(404)(on_404)
    app.errorhandler(500)(on_500)

    init_user_manager(app)
    init_flask_babel(app)
    init_context_processor(app)
    init_app_logger(app, 'frontend-error.log')

    @app.route('/favicon.ico')
    def favicon_ico():
        return send_file('static/favicon.ico')

    return app


def init_user_manager(app):
    from flask_user import SQLAlchemyAdapter, UserManager

    from ..core import db
    from ..model import User
    from ..service import userService
    from .. import signals

    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter)
    user_manager.init_app(app)

    import hashlib

    def hash_password(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def generate_password_hash(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def verify_password(self, password, user):
        return self.hash_password(password) == user.password

    def login_manager_usercallback(user_id):
        user_id = int(user_id) if isinstance(user_id, basestring) else int(user_id)
        user_dict = userService.user_by_id(user_id)
        return User(**user_dict)

    user_manager.hash_password = hash_password.__get__(user_manager, UserManager)
    user_manager.generate_password_hash = generate_password_hash.__get__(user_manager, UserManager)
    user_manager.verify_password = verify_password.__get__(user_manager, UserManager)
    user_manager.login_manager.user_callback = login_manager_usercallback


def init_flask_babel(app):
    from flask_babel import Babel
    from flask_user import current_user
    from ..settings import languages, default_lanuage

    babel = Babel(app)

    @babel.localeselector
    def locale_selector():
        locale = None
        user = current_user
        if user.is_authenticated() and user.account is not None:
            locale = user.account.locale
        if not locale:
            locale = request.accept_languages.best_match(languages)
        if not locale or not (locale in languages):
            locale = default_lanuage
        return locale


def init_context_processor(app):
    from .. import datetime_helper
    from ..service import materialService
    from ..model import Material

    def format_datetime(dt, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime_helper.format_utc_to_local_datetime(dt, fmt=fmt)

    def current_materials():
        locale = get_locale()
        return materialService.material_locale_all(locale)

    def material_by_name(material_name):
        locale = get_locale()
        material = Material.by_locale_name(locale, material_name)
        return material

    def _context_processors():
        return dict(format_datetime=format_datetime, current_materials=current_materials,
                    material_by_name=material_by_name)

    app.context_processor(_context_processors)


def on_sa_data_error(e):
    if request.is_xhr:
        return jsonify(dict(success=False, error_code='DB_DATA_ERROR'))
    else:
        return render_template("error/500.html", error=e)


def on_app_error(e):
    if request.is_xhr:
        return jsonify(dict(success=False, error_code=e.error_code))
    else:
        return render_template("error/500.html", error=e)


def on_404(e):
    if request.is_xhr:
        return jsonify(dict(success=False, error_code='NOT_FOUND'))
    else:
        return render_template("error/404.html")


def on_500(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify(dict(success=False, error_code="SERVER_ERROR"))
    else:
        return render_template("error/500.html")




