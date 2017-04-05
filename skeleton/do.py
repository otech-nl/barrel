#!/usr/bin/env python
# coding=utf8
from app import app
from models import Role, User, Company
from barrel import do, security
import begin


########################################

@do.app_context
@begin.subcommand
def add_user(email, password, role_name, company):
    try:
        role = Role.query.filter(Role.name == role_name).one()
    except:
        print("Onbekende rol: %s" % role_name)
        return

    try:
        company_id = int(company)
    except ValueError:
        company_id = Company.query.filter(Company.abbr == company).one().id
    except TypeError:
        company_id = company.id

    User.create(email=email,
        password=password,
        roles=[role],
        company_id=company_id)

########################################


@do.app_context
@begin.subcommand
def seed():
    ''' Add testing data to the database '''
    print('Seeding')

    Role.create(name='admin')
    Role.create(name='mod')
    Role.create(name='user')

    Company.create(
        abbr=u'OTH',
        name=u'OTech Holding BV')
    company = Company.create(
        abbr=u'OTW',
        name=u'OTech BV')

    add_user('steets@otech', 'test123', 'admin', company=Company.get_admin_company())

########################################


@begin.start(cmd_delim='--')
def run():
    pass

########################################
