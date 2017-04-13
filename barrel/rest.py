import flask
from flask_security import login_required


########################################


def enable(app, models=[]):
    try:
        import flask_datatables as datatables
        import flask_restful as rest
    except ImportError as e:
        module = str(e).split()[-1]
        print('Please run "pip install %s"' % module)

    ########################################

    class BarrelRest(rest.Api):

        def __init__(self, app, models):
            rest.Api.__init__(self, app)
            for model in models:
                self.datatables_api(app, model)

        class SecureResource(rest.Resource):
            ''' require login for access to resources '''
            method_decorators = [login_required]

        def datatables_api(self, app, model):
            ''' create an API that is suitable for use with datatables '''
            resource, path, endpoint = datatables.get_resource(self.SecureResource,
                                                               model,
                                                               app.db.session,
                                                               basepath='/api/')
            self.add_resource(resource, path, endpoint=endpoint)

    ########################################

    app.logger.info('Enabling REST API')
    app.rest = BarrelRest(app, models)
    return app.rest

# ########################################


def jsonify(query_result):
    ''' prepare a SQLAlchemy query result for a JSON response '''
    result = [i.to_dict() for i in query_result]
    return flask.jsonify(result)
