from app import app
from flask_datatables import get_resource
from flask_restful import Api, Resource
from os import environ
import models
import controllers  # noqa: F401

########################################

api = Api(app)
for model in [models.Role, models.User]:
    resource, path, endpoint = get_resource(Resource, model, app.db.session,
                                            basepath='/api/')
    api.add_resource(resource, path, endpoint=endpoint)

########################################

if __name__ == '__main__':
    port = int(environ.get("PORT", 5000))  # for compatibility with Scalingo
    app.run(host="0.0.0.0", port=port, threaded=True)

########################################
