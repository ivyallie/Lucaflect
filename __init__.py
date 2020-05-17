from flask import Flask, render_template
import pymysql

from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

class Database:
    def __init__(self):
        host = 'localhost'
        user = 'ivy'
        password = ''
        db = 'lucaflect01'

        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def query(self, querytext):
        self.cur.execute(querytext)
        result = self.cur.fetchall()

        return result

@app.route('/beepers/')
def sql_test():
    def db_query():
        db = Database()
        query = """SELECT * FROM example"""
        bips = db.query(query)
        return bips

    the_beepers = db_query()

    return render_template('sql_test.html', beepers=the_beepers)