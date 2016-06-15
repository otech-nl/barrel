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
        '[in %(pathname)s:%(lineno)d]'
    ))
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.info('Logger configured: %s' % log)

    return app.logger
