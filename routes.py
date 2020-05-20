from flask import render_template, Blueprint

bp = Blueprint('routes', __name__)
from . import db
database = db.Database()

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/beepers/')
def sql_test():

    beepers = database.query("""SELECT * FROM example""")

    return render_template('sql_test.html', beepers=beepers)