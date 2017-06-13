''' test barrel initialization '''


def test_init(app):
    import barrel
    assert isinstance(app, barrel.flask.Flask)


def test_db(app):
    import barrel
    assert isinstance(app.db, barrel.db.SQLAlchemy)


def test_logger(app):
    import logging
    assert isinstance(app.logger, logging.Logger)
