try:
    from flask_mail import Mail, Message
except ImportError as e:
    module = str(e).split()[-1]
    print 'Please run "pip install %s"' % module

########################################

def enable(app):
    app.logger.info('Enabling mail')
    app.mail = Mail(app)
    return app.mail
