''' test barrel database module '''


def setup_module(app):
    import sys
    sys.path.append('skeleton')


def test_security(app, fake):
    from skeleton import do
    from barrel.util.do import initdb
    app.logger.info('DB: %s ' % app.db)
    initdb()
    do.seed()
    with app.app_context():
        for _ in range(10):
            do.User.create(email=fake.email(), password=fake.password(),
                           group=do.Group.get((_ % 2) + 1))
    assert len(do.Group.query.all()) == 2
