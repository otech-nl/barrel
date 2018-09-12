# coding=utf8
from app import app
from datetime import date
from sqlalchemy.orm import backref
import barrel

barrel.forms.enable(app, lang='nl')
db = app.db


########################################


class BaseModel(db.BaseModel, app.forms.FormModelMixin):
    __abstract__ = True

    def get_group_id(self):
        return self.group_id

########################################


class Group(BaseModel):
    name = db.Column(db.Unicode(30), nullable=False)
    abbr = db.Column(db.Unicode(6), nullable=False)

    def __repr__(self):
        return self.abbr

    @staticmethod
    def get_admin_group():
        return Group.query.filter_by(abbr=u'ACME').one()

########################################


barrel.security.bootstrap(app)


class Role(db.Role, db.mixins.CRUD, app.forms.FormModelMixin):
    def get_group_id(self):
        return Group.get_admin_group().id

@db.decorators.add_reference(Group)
class User(db.User, db.mixins.CRUD):

    def get_group_id(self):
        return self.group_id

    def has_access(self, model):
        return self.group_id == model.get_group_id()


barrel.security.enable(app, User, Role)

########################################


class Customership(BaseModel):
    '''
    association object
    http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-object
    '''

    join_date = db.Column(db.Date, default=date.today())


@db.decorators.add_cross_reference(User, x_cls=Customership)
class Company(BaseModel):
    name = db.Column(db.Unicode(30), nullable=False)

    def __repr__(self):
        return '%s: %s' % (self.name, ', '.join([m.user.name for m in self.customerships]))
