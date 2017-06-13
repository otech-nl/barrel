from flask_security import Security, SQLAlchemyUserDatastore, RoleMixin, UserMixin, utils
from sqlalchemy.ext.hybrid import hybrid_property

########################################


def bootstrap(app):  # noqa: C901  too complex
    ''' prepare abstract Role and User classes '''
    db = app.db

    class Role(db.BaseModel, RoleMixin):
        __abstract__ = True

        name = db.Column(db.String(80), unique=True)

        def __repr__(self):
            return self.name

    db.Role = Role

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

        @staticmethod
        def encrypt_password(plaintext):
            return utils.encrypt_password(plaintext)

        @password.setter
        def _set_password(self, plaintext):
            self._password = self.encrypt_password(plaintext)

        def __repr__(self):
            return self.email

        def get_role(self):
            if len(self.roles.all()) > 1:
                raise ValueError('Cannot get single role for user who has many')
            return self.roles[0]

        @hybrid_property
        def role_id(self):
            return self.role.id

        def has_access(self, model):
            ' (dummy) returns true if user has access to model '
            return true

        def get_permission(self, model=None):
            ' returns either ro (read only), rw (read write) or - (none)'
            if self.has_role('admin'):
                return 'rw'
            elif self.has_role('mod'):
                if model:
                    if self.has_access(model):
                        return 'rw'
                    else:
                        return '-'
                else:
                    return 'rw'
            elif self.has_role('bestuur'):
                if not model or self.has_access(model):
                    return 'ro'
                else:
                    return '-'

    db.User = User


def enable(app, user_class, role_class):
    app.logger.info('Enabling security')
    user_class.add_cross_reference(role_class)

    # configure security with role and user classes
    user_datastore = SQLAlchemyUserDatastore(app.db, user_class, role_class)
    app.security = Security(app, user_datastore)
    app.security.user_datastore = user_datastore

    return app.security
