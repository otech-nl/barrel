import barrel

app = barrel.init('union')
barrel.forms.enable(app, lang='nl', date_format='%Y-%m-%d')


if app.config['DEBUG']:
    from flask import request

    @app.before_request
    def report_start():
        app.logger.report('>>> Start %s' % request.full_path)
        return None

    @app.after_request
    def report_end(response):
        app.logger.report('<<< End   %s' % request.full_path)
        return response
