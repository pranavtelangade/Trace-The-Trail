import os
import logging
from dotenv import load_dotenv
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import ast
from project.core import models
from flask import session, redirect, url_for
from functools import wraps


load_dotenv()

APP = None
WORKER_ID = 0
LOG = logging


def login_required(protected_view):
    @wraps(protected_view)
    def protected_view_wrapper(*args, **kwargs):
        username = session.get('logged_in')
        if username ==True:
            return protected_view(*args, **kwargs)
        return redirect(url_for('view.validate_user'))
    return protected_view_wrapper


def uwsgi_friendly_setup(app):
    global WORKER_ID

    try:
        import uwsgi
        WORKER_ID = uwsgi.worker_id()
    except ImportError:
        # During development on local machine, we may use `flask run` command
        # in this case, uwsgi package won't be available and it will throw error
        pass


def init_logger(app):
    """
    Initializing the logging functionality within the app context
    :param app:
    :return: None
    """
    global LOG
    if not os.path.exists(os.getenv('LOGS_INODE')):
        os.mkdir(os.getenv('LOGS_INODE'))
    log_file = os.path.join(os.getenv('LOGS_INODE'), 'backend.log')
    log_level = logging.DEBUG
    log_format = Formatter(f"[%(asctime)s][worker-{WORKER_ID}][%(levelname)s] %(message)s")

    TWO_MEGABYTE = 2_000_000
    file_handler = RotatingFileHandler(filename=log_file, maxBytes=TWO_MEGABYTE, backupCount=10)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    LOG = app.logger
    # print(app.logger.isEnabledFor(log_level))
    LOG.info('Initialized logger with level %s for worker %s', log_level, WORKER_ID)


def init_cors(app):
    CORS(app=app, origins=ast.literal_eval(os.getenv('CORS_ORIGIN_WHITELIST')), allow_headers=ast.literal_eval(os.getenv('CORS_HEADERS')))
    LOG.info('Initialized CORS')


def init_routes(app):
    from .apps.face_detection.views import onboarding_view, detection_views
    app.register_blueprint(onboarding_view.bp)
    app.register_blueprint(detection_views.bp)


def create_app():
    global APP

    if APP is not None:
        return APP

    APP = Flask(__name__, static_url_path='/static')
    APP.debug = True

    uwsgi_friendly_setup(APP)
    APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=1, x_host=1)
    APP.secret_key = os.getenv('SECRET_KEY')
    init_logger(APP)
    try:
        models.init_app(APP)
        init_routes(APP)
        init_cors(APP)
    except Exception as e:
        LOG.error('An error happened during initializing app components: %s', e)
        raise

    APP.logger.info('App Initialization is finished successfully')
    return APP
