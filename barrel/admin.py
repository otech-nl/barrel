""" Wrapper around Flask-Admin """
import flask
from flask_admin.contrib import sqla
from flask_security import current_user


try:
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
except ImportError as e:
    module = str(e).split()[-1]
    print('Please run "pip install %s"' % module)

########################################


class SecureModelView(sqla.ModelView):

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role('admin')

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                flask.abort(403)
            else:
                # login
                return flask.redirect(flask.url_for('security.login', next=flask.request.url))


########################################


def enable(app, models, model_view=SecureModelView):
    """ Anable Flask-Admin.

    Available as app.admin.

    Args:
        app (Flask app): app.admin is set
        models (list of SQLAlchemy models): models to be accessible through Flask-Admin
    """
    app.logger.info('Enabling admin interface')
    app.admin = Admin(app, name=app.name)
    for model in models:
        add_model(app, model, model_view)
    return app.admin


def add_model(app, model, model_view=SecureModelView):
    """ Add a model to Flask-Admin.

    Args:
        app (Flask app)
        model (SQLAlchemy model)
    """
    app.admin.add_view(model_view(model, app.db.session))
