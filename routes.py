from flask import render_template, Blueprint, current_app, app

bp = Blueprint('routes', __name__)
from . import db
database = db.Database()

@bp.route('/')
def index():
    pageheader="Index"
    return render_template('basis.html')


@bp.route('/beepers/')
def sql_test():
    def db_query():
        sqlquery = """SELECT * FROM example"""
        bips = database.query(sqlquery)
        return bips

    the_beepers = db_query()

    return render_template('sql_test.html', beepers=the_beepers)