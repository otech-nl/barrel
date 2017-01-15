# coding=utf8
from app import app
from datetime import datetime
from flask_security import RoleMixin
from flask_security import current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import backref
from sqlalchemy.sql import func, desc
from sqlalchemy.types import TypeDecorator
import barrel

db = app.db


########################################


class EuroType(TypeDecorator):
    # TODO: improve money handling (default precision, custom WTF field)
    impl = db.Numeric

########################################


class BaseModel(db.BaseModel, db.CRUDMixin, app.forms.FormModelMixin):
    __abstract__ = True

    def get_company_id(self):
        return self.company_id

########################################

barrel.security.bootstrap(app)

user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                      db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(BaseModel, RoleMixin):
    name = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return self.name

########################################


class User(db.User, db.CRUDMixin):
    roles = db.relationship(
        'Role',
        secondary=user_roles,
        backref=db.backref('users', lazy='dynamic'))

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    company = db.relationship("Company",
                                 backref=backref("users", cascade='save-update, merge, delete'))

    def has_access(self, model):
        return self.company_id == model.get_company_id()

    def get_permission(self, model=None):
        if self.has_role('admin'):
            return 'rw'
        elif self.has_role('mod'):
            if model:
                if self.has_access(model):
                    return 'rw'
                else:
                    return '-'
            else:
                return 'ro'
        elif self.has_role('bestuur'):
            if not model or self.has_access(model):
                return 'ro'
            else:
                return '-'

barrel.security.enable(app, user_class=User, role_class=Role)

########################################


class AdresMixin(object):
    straat = db.Column(db.Unicode(80))
    huisnummer = db.Column(db.Integer())
    toevoeging = db.Column(db.Unicode(8))
    postcode = db.Column(db.String(8))
    plaats = db.Column(db.Unicode(80))
    land = db.Column(db.Unicode(20))


class PersonaliaMixin(AdresMixin):
    telefoon = db.Column(db.String(20))
    mobiel = db.Column(db.String(20))
    email = db.Column(db.String(50))

########################################


class NumberMixin(object):
    number = db.Column(db.Integer())

    @classmethod
    def next_number(cls):
        nr = app.db.session.query(func.max(cls.number)).scalar()
        return nr+1 if nr else 1

########################################

status = 'open,active,closed'.split(',')


class Company(BaseModel, AdresMixin, NumberMixin):
    name = db.Column(db.Unicode(30), nullable=False)
    abbr = db.Column(db.Unicode(6), nullable=False)
    status = db.Column(db.Enum(*status))

    def __repr__(self):
        return self.abbr

########################################
