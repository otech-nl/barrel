import flask
from flask_security import current_user
from flask_security.core import AnonymousUser
from os import getcwd, path
import logging

########################################

def enable(app):
    if app.config['LOGGER_NAME'] == app.name:
        app.config['LOGGER_NAME'] = './%s.log' % app.name
    log = path.join(getcwd(), app.config['LOGGER_NAME'])
    file_handler = logging.FileHandler(log)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        # '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.info('Enabled logger: %s' % log)

    def report(msg, level='info', details=''):
        if current_user and not isinstance(current_user, AnonymousUser):
            user = '[%s] ' % current_user
        if details: details = ' (%s)' % details
        msg = '%s%s%s' % (user or '', msg, details)
        print msg
        if level == 'error':
            app.logger.error(msg)
        elif level == 'warning':
            app.logger.warning(msg)
        else:
            app.logger.info(msg)
    app.logger.report = report

    def flash(msg, level='info', details=''):
        flask.flash(msg, level)
        report(msg, level, details)
    app.logger.flash = flash


    return app.logger
