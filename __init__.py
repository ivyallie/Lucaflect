from flask import Flask, render_template
import pymysql

from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

from . import db
database = db.Database()

@app.route('/beepers/')
def sql_test():
    def db_query():
        sqlquery = """SELECT * FROM example"""
        bips = database.query(sqlquery)
        return bips

    the_beepers = db_query()

    return render_template('sql_test.html', beepers=the_beepers)