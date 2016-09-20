from flask import request
from flask_wtf import Form
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError
from wtforms_alchemy import model_form_factory

########################################

class BarrelForms(object):

    ModelForm = model_form_factory(
            Form,
            date_format='%d-%m-%Y',
            datetime_format='%d-%m-%Y %H:%M')

    class FormModelMixin(object):
        @classmethod
        def _get_form(cls):
            class FormClass(BarrelForms.ModelForm):
                class Meta:
                    model = cls
            return FormClass

        @classmethod
        def get_form(cls):
            return cls._get_form()

    ########################################

    def __init__(self, app):
        self.app = app

    ########################################

    def handle_form(self, model_class, form_class=None, model=None, **kwargs):
        form_class = form_class or model_class.get_form()
        form = form_class(request.form, obj=model)
        if form.validate_on_submit():
            kwargs.update(form.data)
            try:
                if model:
                    model.update(**kwargs)
                    self.app.logger.flash('Gegevens opgeslagen', 'success')
                else:
                    print kwargs
                    model_class.create(**kwargs)
                    self.app.logger.flash('Nieuwe gegevens opgeslagen', 'success')
            except SQLAlchemyError as e:
                self.app.db.session.rollback()
                self.app.logger.flash('%s (See log for details)' % e.message, 'error', e)
        else:
            if request.method == 'POST':
                self.app.logger.flash('Gegevens onjuist', 'error', form.errors)
        return form

    ########################################

    @staticmethod
    def breadcrums(obj):
        bc = []
        parent = obj.parent()
        if parent:
            bc = BarrelForms.breadcrums(parent)
        bc.append(dict(route=obj.__class__.__name__.lower(), id=obj.id, name=str(obj)))
        return bc

########################################

def enable(app):
    app.logger.info('Enabling forms')
    app.forms = BarrelForms(app)
    return app.forms

########################################

