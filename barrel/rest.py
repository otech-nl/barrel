import flask
try:
    from flask_restless import APIManager
except ImportError as e:
    module = str(e).split()[-1]
    print('Please run "pip install %s"' % module)

default_methods = ['GET', 'PUT', 'POST', 'DELETE']

########################################


def enable(app, models=[], default_methods=default_methods, **kwargs):
    app.logger.info('Enabling REST API')
    app.api = APIManager(app, flask_sqlalchemy_db=app.db, **kwargs)
    for model in models:
        app.api.create_api(model, methods=default_methods)
    return app.api

# ########################################


def jsonify(payload):
    result = dict(objects=payload)
    return flask.jsonify(result)
