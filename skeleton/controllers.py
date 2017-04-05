from app import app
from flask import redirect, render_template, request, url_for
from flask_security import current_user, login_required, utils as security, roles_accepted
import barrel
import models
import wtforms


def SelectField(model, label_field='name', label=None, **kwargs):
    choices = [(c.id, getattr(c, label_field)) for c in model.query.order_by(label_field)]
    return wtforms.SelectField(label,
                               choices=choices,
                               coerce=int,
                               **kwargs
    )

########################################


@app.route('/')
@login_required
def home():
    return render_template('base.jinja2')

########################################

@app.route('/user/', defaults={'id': None})
@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id):
    user = models.User.get(id) if id else None
    roles = models.Role.query.filter(models.Role.id >= current_user.roles[0].id).all()

    class UserForm(barrel.forms.Form):
        email = wtforms.StringField("email", [
            wtforms.validators.Required()
        ])
        role = wtforms.SelectField(choices=[(r.id, r.name) for r in roles],
                                   default=user.roles[0].id if user else 0)
        active = wtforms.BooleanField(default=True)
        new_password = wtforms.PasswordField()
        confirm_password = wtforms.PasswordField(None, [
            wtforms.validators.EqualTo('new_password',
                                       message='Passwords must match')
        ])
    if current_user.has_role('admin'):
        if user:
            UserForm.company_id = SelectField(models.Company, label='company', default=user.company_id)
        else:
            UserForm.company_id = SelectField(models.Company, label='company')
    elif id:
        UserForm.password = wtforms.PasswordField('Huidig wachtwoord',
                                                  [wtforms.validators.Required()])
    if request.method == 'POST':
        form = request.form
        if user and not current_user.has_role('admin'):
            if not security.verify_password(form.get('current_password'), user.password):
                app.logger.flash("Password incorrect", 'error')

        kwargs = {kw: form.get(kw) for kw in 'email active'.split()}
        if form.get('new_password'):
            kwargs['password'] = form.get('new_password')
        if form.get('role'):
            kwargs['roles'] = [models.Role.get(int(form.get('role')))]
        if form.get('company_id'):
            kwargs['company_id'] = int(form.get('company_id'))
        else:
            kwargs['company_id'] = current_user.company_id

        if user:
            user.update(**kwargs)
        else:
            user = models.User.create(**kwargs)
        return redirect(url_for('user', id=user.id))
    else:
        columns='email role active'
        users = models.User.query
        if current_user.has_role('admin'):
            columns += ' company'
        else:
            users = users.filter_by(company_id=current_user.company_id)
        return app.forms.render_page(
            id,
            models.User,
            template='lists/base.jinja2',
            columns=columns,
            form_class=UserForm,
            rows=users)

########################################


@app.route('/role/', defaults={'id': None})
@app.route('/role/<int:id>', methods=['GET', 'POST'])
@roles_accepted('admin')
def role(id):
        return app.forms.render_page(
            id,
            models.Role,
            template='lists/base.jinja2',
            rows=models.Role.query.all(),
            columns='name'
        )

########################################


@app.route('/profiel')
@login_required
def profiel():
    return render_template('base.jinja2')

########################################


@app.route('/action/<model>/<action>/', defaults=dict(id=0))
@app.route('/action/<model>/<action>/<int:id>')
@login_required
def action(model, action, id):
    if action == 'delete':
        from sys import modules
        cls = getattr(modules['models'], model[:1].upper() + model[1:])
        obj = cls.query.get(id)
        obj.delete()
    else:
        app.logger.flash("Onbekende actie '%s' op %s %s" % (action, model, id),
                         report=False)
    return redirect(request.referrer)

########################################
