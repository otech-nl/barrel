""" some general utilities """
import functools
import sqlalchemy

########################################


class app_context(object):
    """ decorator to add app.app_context """

    def __init__(self, app):
        self.app = app

    def __call__(self, f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            with self.app.app_context():
                return f(*args, **kwargs)
        return decorated_function

########################################
