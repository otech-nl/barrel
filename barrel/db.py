""" Wrapper around Flask-SQLAngelo """
from sqlangelo import SQLAngelo


def enable(app, debug=False):  # noqa: C901
    """ Enable this Flask-SQLAlchemy.

    Available through app.db.
    Provides app.db.BaseModel with should be used as superclass for all models.

    Args:
        app (Flask app)
        debug (boolean): if true, logs extra debugging information
    """
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri == 'default':
        db_uri = 'sqlite:///%s.db' % app.name

    app.db = SQLAngelo(app, db_uri, debug)  # session_options={'autocommit': False, 'autoflush': False}
