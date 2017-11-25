#!/usr/bin/env python
from app import app
from models import Role, User, Group
from barrel.util import app_context
import barrel
import begin


########################################

@app_context(app)
@begin.subcommand
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

    User.create(email=email,
                password=password,
                roles=[role],
                group_id=group_id)

########################################


@app_context(app)
@begin.subcommand
def init():
    ''' Initialize the database '''
    print('Initializing')
    barrel.db.init(app)

    Role.create(name='admin')
    Role.create(name='mod')
    Role.create(name='user')

    Group.create(
        abbr=u'ACME',
        name=u'Administration, Control and Management Environment')

    add_user('admin', 'nidma', 'admin', group=Group.get_admin_group())

    return 'Database initialized successfully'

########################################


@app_context(app)
@begin.subcommand
def seed():
    ''' Add testing data to the database '''
    print('Seeding')

    return 'Database filled successfully'

########################################


@begin.start(cmd_delim='--')
def run():
    pass

########################################
