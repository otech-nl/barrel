NAME = 'MyBarrelApp'
DEBUG = True

SECRET_KEY = 'v?.`!8P=OX*[D!n25NaAZ8W!A*t<)(@a'
SQLALCHEMY_TRACK_MODIFICATIONS = True
if DEBUG:
    SQLALCHEMY_DATABASE_URI = 'default'
else:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://steets:test123@localhost/%s' % NAME

# SECURITY_CONFIRMABLE = True
SECURITY_TRACKABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = 'J1#HDjB=Brh9Kimc&+zhSqN>L?DF3jc;'
