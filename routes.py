from flask import render_template, Blueprint, current_app, app
from lucaflect.db import query

bp = Blueprint('lucaflect', __name__)

@bp.route('/')
def index():
    pageheader="Index"
    return render_template('basis.html')

@bp.route('/beepers/')
def sql_test():
    sql_query = """SELECT * FROM example"""
    beepers = query(sql_query)
    #beepers = [{"name":"wig","feet":"good"},{"name":"jelly","feet":"bad"}]
    for beeper in beepers:
        print(beeper)
    return render_template('sql_test.html', beepers=beepers)