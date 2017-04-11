from datetime import datetime
from flask import Flask, Blueprint
from werkzeug.routing import BaseConverter, ValidationError

from . import db, forms, logger, rest, security, util  # noqa: F401, E401

########################################

try:
    # enforce system-wide UTF-8 encoding
    import sys
    reload(sys)  # noqa: F821
    sys.setdefaultencoding('utf-8')
except NameError:
    pass  # python3

########################################


def init(name, cfg_obj='cfg'):
    ''' init Barrel '''
    class Barrel(Blueprint):
        def __init__(self, app):
            Blueprint.__init__(self, __name__, __name__,
                               template_folder='templates',
                               static_folder='static/barrel')

    # create and configure Flask app
    app = Flask(name)
    app.register_blueprint(Barrel(app))
    app.config.from_object(cfg_obj)

    # Jinja2 settings
    app.config['NAME'] = app.name  # for use in Jinja2 templates
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # we always want a logger
    logger.enable(app)

    # same for database, if configured
    if 'SQLALCHEMY_DATABASE_URI' in app.config:
        db.enable(app)

    # enable transparent dates in routes
    class DateConverter(BaseConverter):
        """Extracts a ISO8601 date from the path and validates it."""

        regex = r'\d{4}-\d{1,2}-\d{1,2}'

        def to_python(self, value):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError()

        def to_url(self, value):
            return value.strftime('%Y-%m-%d')
    app.url_map.converters['date'] = DateConverter

    return app
