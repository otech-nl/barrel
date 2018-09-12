Barrel Skeleton
===============

The skeleton is a bare bones website using barrel.

To install make sure you are in the `skeleton` directory.

First install javascript dependencies (mainly Bootstrap and Datatables):

::

   cd static
   npm install
   cd ..
   pipenv shell

Then install javascript dependencies (mainly Bootstrap and Datatables):

::

   pipenv install
   flask init
   flask run

Finally, you can add users with `flask add_user steets test123 mod ACME`
