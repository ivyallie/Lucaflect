from flask import Flask, render_template
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL()

app.config.from_pyfile('config.py')
mysql.init_app(app)


@app.route('/beepers')
def sql_test():
    sql_query = """SELECT * FROM example"""
    cur = mysql.connection.cursor(DictCursor)
    cur.execute(sql_query)
    beepers = cur.fetchall()
    for beeper in beepers:
        print(beeper)
    cur.close()
    return render_template('sql_test.html', beepers=beepers)