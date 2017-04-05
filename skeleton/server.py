from app import app
from flask_security import current_user, login_required
import controllers  # noqa: F401
import flask
import flask_datatables as datatables
import flask_restful as rest
import functools
import models
import os

########################################

api = rest.Api(app)


class SecureResource(rest.Resource):
    method_decorators = [login_required]


for model in [models.Company]:
    resource, path, endpoint = datatables.get_resource(SecureResource, model, app.db.session,
                                                       basepath='/api/')
    api.add_resource(resource, path, endpoint=endpoint)


########################################

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # for compatibility with Scalingo
    app.run(host="0.0.0.0", port=port, threaded=True)

########################################
