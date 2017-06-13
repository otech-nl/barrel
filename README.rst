Barrel
#######

    'Lock, stock, and ....'

Intention
==========

Barrel bundles Flask extensions that play nice together.

Barrel is also my way to consolidate Flask/SQLAlchemy tips, tricks, lessons-learned, etc. It is *not* production ready, but please feel free use it as starting point and source of inspiration.

Principles
===========

* Barrel is initialized using `barrel.init`, which returns a Flask app. Configuration is read from `cfg.py`.
* Barrel contsists of components and utilities:
    * Component `foo` is enabled using `barrel.foo.enable(app)`. After that `app.foo` provides access to that extension:
        * admin (uses `flask_admin`)
        * db (uses `flask_sqlalchemy`)
        * forms (uses `flask_wtforms`)
        * logger
        * mail (uses `flask_mail`)
        * rest (uses `flask_restful` and `flask_datatables`)
        * security (uses `flask_security`)
    * Utilities do not depend on the app. They do not need to be enabled.
        * collection
        * excel
