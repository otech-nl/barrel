from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, utils
from sqlalchemy.ext.hybrid import hybrid_property

########################################

def bootstrap(app):
    db = app.db

    class User(db.BaseModel, UserMixin):
        __abstract__ = True

        email = db.Column(db.String(255), unique=True, nullable=False)
        _password = db.Column(db.String(255), nullable=False)
        active = db.Column(db.Boolean(), default=True)
        confirmed_at = db.Column(db.DateTime())
        last_login_at = db.Column(db.DateTime())
        current_login_at = db.Column(db.DateTime())
        last_login_ip = db.Column(db.String(255))
        current_login_ip = db.Column(db.String(255))
        login_count = db.Column(db.Integer, default=0)

        @hybrid_property
        def password(self):
            return self._password

        @password.setter
        def _set_password(self, plaintext):
            self._password = utils.encrypt_password(plaintext)

        def __repr__(self):
            return self.email

    db.User = User

def enable(app, user_class, role_class=None):
    app.logger.info('Enabling security')
    user_datastore = SQLAlchemyUserDatastore(app.db, user_class, role_class)
    app.security = Security(app, user_datastore)
    app.security.user_datastore = user_datastore

    return app.security

def add_user(app, email, password, role, **extra):
    user = app.security.user_datastore.create_user(email=email, password=password)
    user.add_role(role)
    return user

