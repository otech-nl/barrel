import flask
from flask_security import current_user
from flask_security.core import AnonymousUser
from os import getcwd, path
import logging
import sys
import traceback

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
    # app.logger already exists, so we just configure it
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.info('Enabled logger: %s' % log)

    def report(msg, level='info', details=''):
        ''' log messages in a standardized fashion '''
        user = ''
        if current_user and not isinstance(current_user, AnonymousUser):
            user = '[%s] ' % current_user
        if details:
            details = ' (%s)' % details
        msg = '%s%s%s' % (user, msg, details)
        print(msg)
        if level == 'error':
            app.logger.error(msg)
        elif level == 'warning':
            app.logger.warning(msg)
        else:
            app.logger.info(msg)
    app.logger.report = report

    def flash(msg, level='info', details='', report=True):
        ''' send a message to the end user '''
        flask.flash(msg, level)
        if report:
            app.logger.report(msg, level, details)
            if hasattr(sys, 'exc_traceback'):
                app.logger.report(msg, level, ''.join(traceback.format_tb(sys.exc_traceback)))
    app.logger.flash = flash

    return app.logger
