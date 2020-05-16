from flask import current_app
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

mysql = MySQL()

def query(query_text):
    mysql.init_app(current_app)
    cur = mysql.connection.cursor(DictCursor)
    cur.execute(query_text)
    result = cur.fetchall()
    cur.close()
    return result

#def init_db():

