import flask
from flask_security import login_required
try:
    import flask_datatables as datatables
    import flask_restful as rest
except ImportError as e:
    module = str(e).split()[-1]
    print('Please run "pip install %s"' % module)

########################################


class SecureResource(rest.Resource):
    method_decorators = [login_required]

########################################


def datatables_api(app, model):
    resource, path, endpoint = datatables.get_resource(SecureResource, model, app.db.session,
                                                       basepath='/api/')
    app.api.add_resource(resource, path, endpoint=endpoint)


########################################


def enable(app, models=[]):
    app.logger.info('Enabling REST API')
    app.api = rest.Api(app)
    app.api.datatables_api = datatables_api
    for model in models:
        app.api.datatables_api(app, model)
    return app.api

# ########################################


def jsonify(query_result):
    result = [i.to_dict() for i in query_result]
    return flask.jsonify(result)
