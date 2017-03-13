from flask import abort, redirect, render_template, request, url_for
from flask_security import current_user
from flask_wtf import FlaskForm as Form
from sqlalchemy.exc import SQLAlchemyError
from wtforms_alchemy import model_form_factory

########################################


class BarrelForms(object):

    class FormModelMixin(object):
        @classmethod
        def get_form(cls):
            class FormClass(BarrelForms.ModelForm):
                class Meta:
                    model = cls
            return FormClass

    ########################################

    def __init__(self, app, messages=None, lang='en', date_format=None, datetime_format=None):
        self.app = app
        self.messages = messages or dict(
            nl=dict(
                updated='Gegevens aangepast',
                created='Nieuwe gegevens opgeslagen',
                error='%s (zie log voor details)',
                illegal='Gegevens onjuist'
            ),
            en=dict(
                updated='Data updated',
                created='New data stored',
                error='%s (see log for detaiils)',
                illegal='Data incorrect'
            )
        )[lang]

        class ModelForm(model_form_factory(Form,
                                           date_format=date_format,
                                           datetime_format=datetime_format)):
            def __iter__(self):
                ''' make the 'only' attribute order-sensitive '''
                field_order = getattr(self, 'only', None)
                if field_order:
                    temp_fields = []
                    for name in field_order:
                        if name == '*':
                            temp_fields.extend([f for f in self._unbound_fields
                                                if f[0] not in field_order])
                        else:
                            temp_fields.append([f for f in self._unbound_fields if f[0] == name][0])
                            self._unbound_fields = temp_fields
                return super(Form, self).__iter__()
        BarrelForms.ModelForm = ModelForm

    ########################################

    def handle_form(self, model_class, form_class=None, model=None, **kwargs):
        form_class = form_class or model_class.get_form()
        form = form_class(request.form, obj=model)
        if form.validate_on_submit():
            self.app.logger.report('Submit: %s' % request.full_path)
            kwargs.update(form.data)
            try:
                if model:
                    model.update(**kwargs)
                    self.app.logger.flash(self.messages['updated'], 'success')
                else:
                    # print kwargs
                    model_class.create(**kwargs)
                    self.app.logger.flash(self.messages['created'], 'success')
            except SQLAlchemyError as e:
                self.app.db.session.rollback()
                self.app.logger.flash(self.messages['error'] % e.message, 'error', e)
        else:
            if request.method == 'POST':
                self.app.logger.flash(self.messages['illegal'], 'error', form.errors)
            else:
                self.app.logger.report('Form: %s' % request.full_path)

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

    def render_page(self, id, model_class, template='lists/base.jinja2',
                    form_class=None, next_page=None, columns='', **kwargs):
        ''' render a list with a form modal '''
        form_class = form_class or model_class.get_form()
        model = model_class.get(id) if id else None
        api = model_class.get_api()

        show_form = (id == 0)
        if api in request.form:  # update
            form = self.handle_form(model_class, form_class, model=model)
            show_form = bool(form.errors)
        elif model:  # edit
            form = form_class(None, obj=model)
            show_form = True
        else:  # new
            form = form_class()

        perm = current_user.get_permission(model)
        if self.app.config['DEBUG']:
            if perm == '-':
                abort(403)
                self.app.logger.report('%s template %s for %s (%s form, %s) with %s' %
                                       (request.method, template, api, 'show' if show_form else 'hide',
                                        perm, pformat(request.form)))
            if form.errors:
                self.app.logger.report('Form errors: %s' % form.errors)
        if not next_page or form.errors:
            return render_template(template,
                                   api=api,
                                   columns=columns.split(),
                                   form=form,
                                   model=model,
                                   readonly=perm == 'ro',
                                   show_form=show_form,
                                   **kwargs)
        else:
            return redirect(next_page)

    ########################################

    def child_form(self, id, model_class, parent_id, parent_class, **kwargs):
        ''' a generic function for a form of a model with a child '''
        api = model_class.get_api()
        parent_api = parent_class.get_api()
        if not id:
            kwargs['%s_id' % parent_api] = parent_id
            obj = model_class.create(naam="Nieuwe %s" % api, **kwargs)
            return redirect(url_for(api, id=obj.id))
        else:
            obj = model_class.get(id)
            parent_id = getattr(obj, '%s_id' % parent_api)
            next_page = url_for(parent_api, id=parent_id) if request.method == 'POST' else None
            kwargs[parent_api] = parent_class.get(parent_id)
            return self.render_page(id, model_class,
                                    template='%s.jinja2' % api,
                                    next_page=next_page,
                                    **kwargs)

########################################


def enable(app, **kwargs):
    app.logger.info('Enabling forms')
    app.forms = BarrelForms(app, **kwargs)
    return app.forms

########################################
