'''
Flask-Barrel
-----------
Flask-Barrel provides scaffolding for your Flask app, based on existing flask
extensions, but with sensible defaults in place.
'''

from setuptools import setup

setup(name='flask_barrel',
      version='1.3',
      description='Lock, stock, and * for your Flask app',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords='flask scaffolding',
      long_description=__doc__,
      url='http://github.com/otech-nl/barrel',
      author='OTech BV',
      author_email='steets@otech.nl',
      license='CC BY-NC-ND',
      packages=['barrel'],
      install_requires=[
          'begins',
          'flask-security',
          'flask-sqlalchemy==2.1',
          'wtforms-alchemy'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'behave', 'faker'],
      test_suite='tests',
      include_package_data=True,
      platforms='any',
      zip_safe=False)
