''' text fixtures '''

from pytest import fixture


@fixture(scope='session')
def app():
    import barrel
    import os

    app = barrel.init('Test', 'tests.cfg')
    return app

@fixture(scope='session')
def fake():
    from faker import Faker
    return Faker()
