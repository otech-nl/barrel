from app import app
import begin
import db
import functools
import security


def app_context(f):
    ''' decorator to add app.app_context '''
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return decorated_function

########################################


@app_context
@begin.subcommand
def initdb():
    ''' Initialize the database '''
    print('Initializing')
    db.init(app)

########################################
