from flask import render_template, Blueprint, current_app, app

bp = Blueprint('routes', __name__)
from . import db
database = db.Database()

@bp.route('/')
def index():
    pageheader="Index"
    return render_template('basis.html')

@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/beepers/')
def sql_test():

    beepers = database.query("""SELECT * FROM example""")

    return render_template('sql_test.html', beepers=beepers)