from flask import request, flash
from flask_wtf import Form
from sqlalchemy.exc import SQLAlchemyError
from wtforms_alchemy import model_form_factory

########################################

def enable(app):
    app.ModelForm = model_form_factory(
        Form,
        date_format='%d-%m-%Y',
        datetime_format='%d-%m-%Y %H:%M')

    class FormModelMixin(object):
        @classmethod
        def get_form(cls):
            class FormClass(app.ModelForm):
                class Meta:
                    model = cls
            return FormClass
    app.db.FormModelMixin = FormModelMixin

########################################

def handle_form(model_class, form_class=None, model=None, **kwargs):
    form_class = form_class or model_class.get_form()
    form = form_class(request.form, obj=model)
    if form.validate_on_submit():
        kwargs.update(form.data)
        try:
            if model:
                model.update(**kwargs)
                flash('Gegevens opgeslagen', 'success')
            else:
                print kwargs
                model_class.create(**kwargs)
                flash('Nieuwe gegevens opgeslagen', 'success')
        except SQLAlchemyError, e:
            flash('%s (See log for details)' % e.message, 'error')
            print str(e)
    else:
        if request.method == 'POST':
            print '##############\n%s\n##############'% form.errors
            flash('Gegevens onjuist', 'error')
            flash('DEBUG: %s' % form.errors, 'error')
    return form

########################################

def breadcrums(obj):
    bc = []
    parent = obj.parent()
    if parent:
        bc = breadcrums(parent)
    bc.append(dict(route=obj.__class__.__name__.lower(), id=obj.id, name=str(obj)))
    return bc

########################################

