DEBUG = True

SECRET_KEY = 'notsosecret'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'default'

# SECURITY_CONFIRMABLE = True
SECURITY_TRACKABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = 'flauw'
