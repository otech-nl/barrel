import barrel

app = barrel.init('barrel')
barrel.forms.enable(app, lang='nl')


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
