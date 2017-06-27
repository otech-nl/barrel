""" wrapper around Flask Restful and Flask Datatables """

import flask
from flask_security import login_required


########################################


try:
    import flask_datatables as datatables
    import flask_restful as rest

    class SecureResource(rest.Resource):
        """ Require login for access to resources. """
        method_decorators = [login_required]

    ########################################

    def datatables_api(app, model):
        """ Create an API that is suitable for use with datatables.

        Args:
            app: Barrel app
            model: SQLAlchemy model
        """
        resource, path, endpoint = datatables.get_resource(SecureResource,
                                                            model,
                                                            app.db.session,
                                                            basepath='/api/')
        app.rest.add_resource(resource, path, endpoint=endpoint)

        ########################################

    def enable(app, models=[]):
        """ enable this module

        Args:
            app: Barrel app
            models: list of SQLAlchemy model
        """
        app.logger.info('Enabling REST API')

        app.rest = rest.Api(app)
        app.rest.SecureResource = SecureResource
        app.rest.datatables_api = datatables_api

        for model in models:
            datatables_api(app, model)

        return app.rest

except ImportError as e:
    module = str(e).split()[-1]
    print('Please run "pip install %s"' % module)

# ########################################


def jsonify(query_result):
    """ prepare a SQLAlchemy query result for a JSON response """
    result = [i.to_dict() for i in query_result]
    return flask.jsonify(result)
