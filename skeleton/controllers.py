from app import app
from flask import redirect, render_template, request, url_for
from flask_security import current_user, login_required, utils as security, roles_accepted, logout_user
import barrel
import models
import wtforms
import do


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
            UserForm.group_id = SelectField(models.Group, label='group', default=user.group_id)
        else:
            UserForm.group_id = SelectField(models.Group, label='group')
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
        if form.get('group_id'):
            kwargs['group_id'] = int(form.get('group_id'))
        else:
            kwargs['group_id'] = current_user.group_id

        if user:
            user.update(**kwargs)
        else:
            user = models.User.create(**kwargs)
        return redirect(url_for('user', id=user.id))
    else:
        columns='email role active'
        users = models.User.query
        if current_user.has_role('admin'):
            columns += ' group'
        else:
            users = users.filter_by(group_id=current_user.group_id)
        return app.forms.render_page(
            id,
            models.User,
            template='lists/base.jinja2',
            columns=columns,
            form_class=UserForm,
            rows=users)

########################################


@app.route('/init/', defaults={'status': None})
@app.route('/init/<status>')
@roles_accepted('admin')
def init(status):
    if status == 'confirmed':
        logout_user()
        do.init()
        return redirect(url_for('security.login'))
    else:
        return render_template('reset.jinja2')

########################################


@app.route('/seed')
@roles_accepted('admin')
def seed():
    do.seed()

########################################


@app.route('/role/', defaults={'id': None})
@app.route('/role/<int:id>', methods=['GET', 'POST'])
@roles_accepted('admin')
def role(id):
        return app.forms.render_page(
            id,
            models.Role,
            template='lists/base.jinja2',
            columns='name'
        )

########################################


@app.route('/group/', defaults={'id': None})
@app.route('/group/<int:id>', methods=['GET', 'POST'])
@roles_accepted('admin')
def group(id):
        return app.forms.render_page(
            id,
            models.Group,
            template='lists/base.jinja2',
            columns='abbr name'
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
