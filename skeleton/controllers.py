from app import app
from flask import render_template
from flask_security import login_required
# from helpers import __render_page, child_form, get_groepen
# from sqlalchemy.exc import SQLAlchemyError
# from wtforms_alchemy import QuerySelectField
# import barrel
# import models
# import wtforms
# import reports  # noqa: F401

########################################


@app.route('/')
@login_required
def home():
    return render_template('base.jinja2')

########################################


@app.route('/gebruiker')
@login_required
def user():
    return render_template('base.jinja2')

########################################


@app.route('/rol')
@login_required
def role():
    return render_template('base.jinja2')

########################################


@app.route('/profiel')
@login_required
def profiel():
    return render_template('base.jinja2')

########################################
