from datetime import datetime
import flask
from werkzeug.routing import BaseConverter, ValidationError
import jinja2
from . import admin, db, forms, logger, mail, rest, security, util  # noqa: F401, E401

########################################

try:
    # enforce system-wide UTF-8 encoding
    import sys
    reload(sys)  # noqa: F821
    sys.setdefaultencoding('utf-8')
except NameError:
    pass  # python3


__current_app = None

########################################


def init(name, cfg_obj='cfg'):
    ''' init Barrel '''
    global __current_app
    if __current_app:
        # singleton
        return __current_app

    class Barrel(flask.Blueprint):
        def __init__(self, app):
            flask.Blueprint.__init__(self, __name__, __name__,
                                     template_folder='templates',
                                     static_folder='static/barrel')

    # create and configure Flask app
    __current_app = app = flask.Flask(name)
    app.register_blueprint(Barrel(app))
    app.config.from_object(cfg_obj)

    # Jinja2 settings
    app.config['NAME'] = app.name  # for use in Jinja2 templates
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # for debugging
    @jinja2.contextfunction
    def get_context(c):
        return c

    app.jinja_env.globals['context'] = get_context
    app.jinja_env.globals['callable'] = callable

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
