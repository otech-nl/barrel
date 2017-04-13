#!/usr/bin/env python
# coding=utf8
from models import Role, User, Group
from barrel.util import do
import begin


########################################

@do.app_context
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


@do.app_context
@begin.subcommand
def seed():
    ''' Add testing data to the database '''
    print('Seeding')

    Role.create(name='admin')
    Role.create(name='mod')
    Role.create(name='user')

    Group.create(
        abbr=u'OTH',
        name=u'OTech Holding BV')
    group = Group.create(
        abbr=u'OTW',
        name=u'OTech BV')

    add_user('steets@otech', 'test123', 'admin', group=Group.get_admin_group())

########################################


@begin.start(cmd_delim='--')
def run():
    pass

########################################
