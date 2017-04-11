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

        @password.setter
        def _set_password(self, plaintext):
            self._password = utils.encrypt_password(plaintext)

        def __repr__(self):
            return self.email

        @hybrid_property
        def role(self):
            return self.roles[0]

        def has_access(self, model):
            ' (dummy) returns true if user has access to model '
            return self.company_id == model.get_company_id()

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
    db = app.db
    # create an m:n relation between users and roles
    user_roles = db.Table('user_roles',
                          db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                          db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))
    user_class.roles = db.relationship(
        'Role',
        secondary=user_roles,
        backref=db.backref('users', lazy='dynamic'))

    # configure security with role and user classes
    user_datastore = SQLAlchemyUserDatastore(app.db, user_class, role_class)
    app.security = Security(app, user_datastore)
    app.security.user_datastore = user_datastore

    return app.security
