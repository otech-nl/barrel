import arrow
from flask import jsonify, Blueprint, request
from flask.ext import restless
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import utils as su
import jinja2
import logging
from os import getcwd, path
from werkzeug.exceptions import default_exceptions, HTTPException
from sqlalchemy.orm import class_mapper, ColumnProperty
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy_utils as sau

from flask_wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms import PasswordField, validators

########################################

class Barrel(Blueprint):

    def __init__(self, app):
        Blueprint.__init__(self, __name__, __name__,
            template_folder='templates',
            static_folder='templates')
        app.register_blueprint(self)
        self.app = app
        app.config.from_object('cfg')

        self.enable_logger()
        app.logger.info('App name: %s' % app.name)

        if 'SQLALCHEMY_DATABASE_URI' in app.config:
            self.enable_db()

    ########################################

    def enable_logger(self):
        app = self.app
        if app.config['LOGGER_NAME'] == app.name:
            app.config['LOGGER_NAME'] = '%s.log' % app.name
        log = path.join(getcwd(), app.config['LOGGER_NAME'])
        file_handler = logging.FileHandler(log)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        app.logger.handlers = []
        app.logger.addHandler(file_handler)
        app.logger.info('Logger configured: %s' % log)

        return app.logger

    ########################################

    def enable_db(self):
        app = self.app
        if app.config['SQLALCHEMY_DATABASE_URI'] == 'default':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % app.name
        app.logger.info('Enabling DB with %s' % app.config['SQLALCHEMY_DATABASE_URI'])

        app.db = SQLAlchemy(app)
        db = app.db

        db.echo = app.config['DEBUG']

        class CRUDMixin(object):
            @classmethod
            def create(cls, commit=True, **kwargs):
                instance = cls(**kwargs)
                return instance.save(commit=commit)

            @classmethod
            def get(cls, id):
                return cls.query.get(id)

            @classmethod
            def get_or_404(cls, id):
                return cls.query.get_or_404(id)

            def update(self, commit=True, **kwargs):
                for attr, value in kwargs.iteritems():
                    setattr(self, attr, value)
                return commit and self.save() or self

            def save(self, commit=True):
                db.session.add(self)
                if commit:
                    db.session.commit()
                return self

            def delete(self, commit=True):
                db.session.delete(self)
                return commit and db.session.commit()

        class BaseModel(db.Model, CRUDMixin):
            ''' used as super model for all other models '''
            __abstract__ = True

            id = db.Column(db.Integer, primary_key=True)

            @classmethod
            def columns(cls):
                return cls.__table__.columns.keys()

            @classmethod
            def from_form(cls, form):
                obj = cls()
                form.populate_obj(obj)
                return obj

            @classmethod
            def get_form(cls):
                class FormClass(app.ModelForm):
                    class Meta:
                        model = cls
                return FormClass

            def to_dict(self):
                return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        db.BaseModel = BaseModel

        return db

    def init_db(self):
        self.app.logger.info('Initializing DB')
        self.app.db.create_all()

    def commit(self):
        self.app.db.session.commit()

    ########################################

    def enable_json_errors(self):
        """
        All error responses that you don't specifically
        manage yourself will have application/json content
        type, and will contain JSON like this (just an example):

        { "message": "405: Method Not Allowed" }
        """
        app = self.app
        app.logger.info('Enabling JSON errors')

        def make_json_error(ex):
            response = jsonify(message=str(ex))
            response.status_code = (ex.code
                                    if isinstance(ex, HTTPException)
                                    else 500)
            app.logger.error(str(ex))
            return response

        for code in default_exceptions.iterkeys():
            app.error_handler_spec[None][code] = make_json_error

    ########################################

    def enable_admin(self, models):
        app = self.app
        app.logger.info('Enabling admin interface')
        app.admin = Admin(app, name=app.name)
        for model in models:
            self.add_admin_model(model)
        return app.admin

    def add_admin_model(self, model):
        self.app.admin.add_view(ModelView(model, self.app.db.session))

    ########################################

    default_methods = ['GET', 'PUT', 'POST', 'DELETE']
    def enable_rest(self, models=[], default_methods=default_methods, **kwargs):
        app = self.app
        app.logger.info('Enabling REST API')
        app.api = restless.APIManager(app, flask_sqlalchemy_db=app.db, **kwargs)
        for model in models:
            self.app.api.create_api(model, methods=default_methods)
        return app.api

    @staticmethod
    def return_json(payload):
        result = dict(objects=payload)
        return jsonify(result)

    ########################################

    def enable_security(self, user_class=None, role_class=None):
        app = self.app
        db = app.db
        roles_users = db.Table('roles_users',
                db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

        class Role(db.BaseModel, RoleMixin):
            name = db.Column(db.String(80), unique=True)
            description = db.Column(db.String(255))

            def __repr__(self):
                return self.description

        class User(db.BaseModel, UserMixin):
            email = db.Column(db.String(255), unique=True, nullable=False)
            _password = db.Column(db.String(255), nullable=False)
            active = db.Column(db.Boolean())
            confirmed_at = db.Column(db.DateTime())
            last_login_at = db.Column(db.DateTime())
            current_login_at = db.Column(db.DateTime())
            last_login_ip = db.Column(db.String(255))
            current_login_ip = db.Column(db.String(255))
            login_count = db.Column(db.Integer)
            roles = db.relationship(
                'Role',
                secondary=roles_users,
                backref=db.backref('users', lazy='dynamic'))

            @hybrid_property
            def password(self):
                return self._password

            @password.setter
            def _set_password(self, plaintext):
                self._password = su.encrypt_password(plaintext)

            def __repr__(self):
                return self.email

            def add_role(self, role_name):
                role = Role.query.filter_by(name=role_name).first()
                self.roles.append(role)

        # ugly way to set defaults, needed because User and Role are not defined yet
        user_class = user_class or User
        role_class = role_class or Role
        user_datastore = SQLAlchemyUserDatastore(db, user_class, role_class)
        app.security = Security(app, user_datastore)
        app.security.user_datastore = user_datastore
        app.security.Role = Role
        app.security.User = User

        return app.security

    def add_user(self, email, password, role, **extra):
        user = self.app.security.user_datastore.create_user(email=email, password=password)
        user.add_role(role)
        return user

    ########################################

    def enable_forms(self):

        self.app.ModelForm = model_form_factory(
            Form,
            date_format='%Y-%m-%d',
            datetime_format='%Y-%m-%d %H:%M')

    @staticmethod
    def handle_form(modelCls, formCls=None, model=None, **kwargs):
        if not formCls:
            formCls = modelCls.get_form()
        form = formCls(request.form, obj=model)
        if form.validate_on_submit():
            if model:
                form.populate_obj(obj=model)
                model.update(form)
            else:
                kwargs.update(form.data)
                modelCls.create(**kwargs)
        # else:
        #     print '!!!!!!!!!!!!!!! not valid: %s' % model
        #     for field, value in form.data.iteritems():
        #         print '   %s: %s'% (field, value)
        return form

    @staticmethod
    def breadcrums(obj):
        breadcrums = []
        parent = obj.parent()
        if parent:
            breadcrums = Barrel.breadcrums(parent)
        breadcrums.append(dict(route=obj.__class__.__name__.lower(), id=obj.id, name=str(obj)))
        return breadcrums

########################################

