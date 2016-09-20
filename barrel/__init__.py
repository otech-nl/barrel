from flask import Flask, Blueprint

import admin
import db
import forms
import logger
import mail
import rest
import security

########################################

import sys
reload(sys)
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

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    logger.enable(app)
    app.logger.info('App name: %s' % app.name)

    # if 'DEBUG' in app.config and app.config['DEBUG']:
    #     from flask_debugtoolbar import DebugToolbarExtension
    #     DebugToolbarExtension(app)

    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db.enable(app)

    return app

