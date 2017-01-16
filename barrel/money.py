from wtforms import fields, widgets
import sqlalchemy


class MoneyWidget(widgets.Input):
    unit = '&euro;'

    def __init__(self):
        self.input_type = 'number'

    def __call__(self, field, **kwargs):
        return '<div class="input-group"><span class="input-group-addon">%s</span>%s</div>'\
               % (self.unit, super(MoneyWidget, self).__call__(field, **kwargs))


class MoneyField(fields.Field):
    widget = MoneyWidget


class MoneyType(sqlalchemy.Numeric):

    def __init__(self, **kwargs):
        kwargs.setdefault('precision', 4)
        kwargs.setdefault('scale', 2)
        super(MoneyType, self).__init__(**kwargs)
