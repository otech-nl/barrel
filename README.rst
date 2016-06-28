Barrel
#######

    'Lock, stock, and ....'

Intention
==========

Barrel intends to extend Flask with extensions that play nice together.

Principles
===========

* Barrel is initialized using `barrel.init`, which returns a Flask app.
* Barrel contsists of components and utilities:
    * Component `foo` is enabled using `barrel.foo.enable(app)`. After that `app.foo` provides access to that extension:
        * admin (based on `flask_admin`)
        * db
        * forms
        * logger
        * mail
        * rest
        * security
    * Utilities do not depend on the app. They do not need to be enabled.
        * collection
        * excel
