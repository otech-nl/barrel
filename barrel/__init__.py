from flask import Flask, Blueprint

import db
import forms  # noqa: F401
import logger
import security  # noqa: F401

########################################

import sys
reload(sys)  # noqa: F821
sys.setdefaultencoding('utf-8')

########################################


def init(name):
    class Barrel(Blueprint):
        def __init__(self, app):
            Blueprint.__init__(self, __name__, __name__,
                               template_folder='templates',
                               static_folder='static/barrel')
    app = Flask(name)
    app.register_blueprint(Barrel(app))
    app.config.from_object('cfg')

    app.config['NAME'] = app.name  # for use in Jinja2 templates
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    logger.enable(app)
    app.logger.info('App name: %s' % app.name)

    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db.enable(app)

    return app
