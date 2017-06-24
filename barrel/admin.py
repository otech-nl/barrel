""" Wrapper around Flask-Admin """
try:
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
except ImportError as e:
    module = str(e).split()[-1]
    print('Please run "pip install %s"' % module)

########################################


def enable(app, models):
    """ Anable Flask-Admin.

    Args:
        app (Flask app): app.admin is set
        models (list of SQLAlchemy models): models to be accessible through Flask-Admin
    """
    app.logger.info('Enabling admin interface')
    app.admin = Admin(app, name=app.name)
    for model in models:
        add_model(app, model)
    return app.admin


def add_model(app, model):
    """ Add a model to Flask-Admin.

    Args:
        app (Flask app)
        model (SQLAlchemy model)
    """
    app.admin.add_view(ModelView(model, app.db.session))
