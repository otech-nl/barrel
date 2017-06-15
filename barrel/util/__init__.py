from wtforms import fields, widgets
import functools
import sqlalchemy

########################################


class app_context(object):
    ''' decorator to add app.app_context '''

    def __init__(self, app):
        self.app = app

    def __call__(self, f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            with self.app.app_context():
                return f(*args, **kwargs)
        return decorated_function

########################################


class MoneyWidget(widgets.Input):
    unit = '&euro;'

    def __init__(self):
        self.input_type = 'number'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('step', 0.01)
        return '<div class="input-group"><span class="input-group-addon">%s</span>%s</div>'\
               % (self.unit, super(MoneyWidget, self).__call__(field, **kwargs))


class MoneyField(fields.Field):
    widget = MoneyWidget


class MoneyType(sqlalchemy.Numeric):

    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 2)
        super(MoneyType, self).__init__(**kwargs)

########################################


class PercentageWidget(widgets.Input):

    def __init__(self):
        self.input_type = 'number'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('step', 0.01)
        return ('<div class="input-group">%s<span class="input-group-addon">%%</span></div>'
                % (super(PercentageWidget, self).__call__(field, **kwargs)))


class PercentageField(fields.Field):
    widget = PercentageWidget


class PercentageType(sqlalchemy.Numeric):

    def __init__(self, **kwargs):
        kwargs.setdefault('scale', 2)
        super(PercentageType, self).__init__(**kwargs)

########################################
