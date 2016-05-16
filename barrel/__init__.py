from flask import jsonify, Blueprint
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


########################################

class Barrel(Blueprint):

    def __init__(self, app):
        Blueprint.__init__(self, __name__, __name__, template_folder='templates')
        app.register_blueprint(self)
        self.app = app
        app.config.from_object('cfg')

        self.enable_logger()
        app.logger.info('App name: %s' % app.name)

        # app.jinja_loader = jinja2.ChoiceLoader([
        #     app.jinja_loader,
        #     jinja2.FileSystemLoader(['barrel/templates']),
        # ])

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

        class BaseModel(db.Model):
            ''' used as super model for all other models '''
            __abstract__ = True

            id = db.Column(db.Integer, primary_key=True)

            def persist(self):
                db.session.commit();

            def create(self):
                db.session.add(self)
                self.persist()

        db.BaseModel = BaseModel

        return db

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

    def enable_rest(self, models):
        app = self.app
        app.logger.info('Enabling REST API')
        app.api = restless.APIManager(app, flask_sqlalchemy_db=app.db)
        for model, methods in models:
            app.logger.info('   %s' % str(model))
            self.add_rest_model(model, methods)
        return app.api

    def add_rest_model(self, model, methods):
        methods = methods.split()
        self.app.api.create_api(model, methods=methods)

    # def handle_command(cmd):
    #     if cmd == 'all':
    #         return flask.render_template('filter.html')
    #     elif cmd == 'new':
    #         return flask.render_template('form.html')
    #     else:
    #         return "Existing: %s" % cmd

    # models = 'person note appointment task'.split(' ')
    # for model in models:
    #     app.add_url_rule('/%s/' % model, model, handle_command, defaults={'cmd':'all'})
    #     app.add_url_rule('/%s/new' % model, model, handle_command, defaults={'cmd':'new'})
    #     app.add_url_rule('/%s/<cmd>' % model, model, handle_command)

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
            email = db.Column(db.String(255), unique=True)
            password = db.Column(db.String(255))
            active = db.Column(db.Boolean())
            confirmed_at = db.Column(db.DateTime())
            last_login_at = db.Column(db.DateTime())
            current_login_at = db.Column(db.DateTime())
            last_login_ip = db.Column(db.String(255))
            current_login_ip = db.Column(db.String(255))
            login_count = db.Column(db.Integer)
            roles = db.relationship('Role', secondary=roles_users,
                                    backref=db.backref('users', lazy='dynamic'))

            def __repr__(self):
                return self.email

            def add_role(self, role_name):
                role =  Role.query.filter_by(name=role_name).first()
                self.roles.append(role)

        # augly way to set defaults, needed because User and Role are not defined yet
        if not user_class: user_class = User
        if not role_class: role_class = Role
        user_datastore = SQLAlchemyUserDatastore(db, user_class, role_class)
        app.security = Security(app, user_datastore)
        app.security.user_datastore = user_datastore
        app.security.Role = Role
        app.security.User = User

        return app.security

    def add_user(self, email, password):
        return self.app.security.user_datastore.create_user(email=email, password=su.encrypt_password(password))

    ########################################

    def init_db(self):
        self.app.logger.info('Initializing DB')
        self.app.db.create_all()

    def commit(self):
        self.app.db.session.commit()

########################################


