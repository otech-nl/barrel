#!/usr/bin/env python
from app import app
from models import Role, User, Group, Company, Customership
from barrel.util import app_context
import barrel
import click


########################################

@app.cli.command()
@click.argument('email')
@click.argument('password')
@click.argument('role_name')
@click.argument('group')
def add_user(email, password, role_name, group):
    try:
        role = Role.query.filter(Role.name == role_name).one()
    except:
        print("Onbekende rol: %s" % role_name)
        return

    try:
        group_id = int(group)
    except ValueError:
        group_id = Group.query.filter(Group.abbr == group).one().id
    except TypeError:
        group_id = group.id

    return User.create(email=email,
                       password=password,
                       roles=[role],
                       group_id=group_id)

########################################


@app.cli.command()
def init():
    ''' Initialize the database '''
    print('Initializing')
    app.db.init()

    role = Role.create(name='admin')
    Role.create(name='mod')
    Role.create(name='user')

    group = Group.create(
        abbr=u'ACME',
        name=u'Administration, Control and Management Environment')

    user =  User.create(email='admin',
                        password='nimda',
                        role=role,
                        group=group)
    company = Company.create(name='OTech.nl')
    Customership.create(company=company, user=user)

    return 'Database initialized successfully'

########################################
