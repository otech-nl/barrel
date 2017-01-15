#!/usr/bin/env python
# coding=utf8
from app import app
from models import Role, User, Company
import barrel
import begin


def app_context(f):
    ''' decorator to add app.app_context '''
    def decorated_function(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return decorated_function

########################################


@app_context
@begin.subcommand
def add_user(email, password, role_name, company):
    ''' create a new user with these credentials '''
    try:
        company_id = int(company)
    except ValueError:
        company_id = Company.query.filter(Company.abbr == company).one().id
    except TypeError:
        company_id = company.id
    try:
        role = Role.query.filter(Role.name == role_name).one()
    except:
        print("Onbekende rol: %s" % role_name)
        return

    User.create(
        email=email,
        password=password,
        roles=[role],
        company_id=company_id)

########################################


@app_context
@begin.subcommand
def initdb():
    ''' Initialize the database '''
    print('Initializing')
    barrel.db.init(app)

    Role.create(name='admin')
    Role.create(name='mod')
    Role.create(name='user')

    Company.create(
        abbr=u'OTH',
        name=u'OTech Holding BV')
    company = Company.create(
        abbr=u'OTW',
        name=u'OTech BV')

    add_user('steets@otech', 'test123', 'admin', company)

########################################


@app_context
@begin.subcommand
def seed():
    ''' Add testing data to the database '''
    print('Seeding')

########################################


########################################


@begin.start
def run():
    pass

########################################
