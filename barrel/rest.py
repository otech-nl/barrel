import flask
from flask_restless import APIManager

default_methods = ['GET', 'PUT', 'POST', 'DELETE']

########################################

def enable(app, models=[], default_methods=default_methods, **kwargs):
    app.logger.info('Enabling REST API')
    app.api = APIManager(app, flask_sqlalchemy_db=app.db, **kwargs)
    for model in models:
        app.api.create_api(model, methods=default_methods)
    return app.api

# ########################################

# def enable_json_errors(self):
#     """
#     All error responses that you don't specifically
#     manage yourself will have application/json content
#     type, and will contain JSON like this (just an example):

#     { "message": "405: Method Not Allowed" }
#     """
#     app = self.app
#     app.logger.info('Enabling JSON errors')

#     def make_json_error(ex):
#         response = jsonify(message=str(ex))
#         response.status_code = (ex.code
#                                 if isinstance(ex, HTTPException)
#                                 else 500)
#         app.logger.error(str(ex))
#         return response

#     for code in default_exceptions.iterkeys():
#         app.error_handler_spec[None][code] = make_json_error

# ########################################

def jsonify(payload):
    result = dict(objects=payload)
    return flask.jsonify(result)

