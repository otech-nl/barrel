from flask_mail import Mail, Message

########################################

def enable(app):
    app.logger.info('Enabling mail')
    app.mail = Mail(app)
    return app.mail
