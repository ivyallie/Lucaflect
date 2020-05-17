from flask import current_app, g
from flask.cli import with_appcontext
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
import click

mysql = MySQL()

def query(query_text):
    mysql = MySQL()
    mysql.init_app(current_app)
    cur = mysql.connection.cursor(DictCursor)
    cur.execute(query_text)
    result = cur.fetchall()
    cur.close()
    return result

def init_db():
    mysql.init_app(current_app)
    cur = mysql.connection.cursor()
    with current_app.open_resource('schema.sql', 'r') as f:
        for line in f:
            print(line)
            cur.execute(line)
    cur.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB initialized.')

def init_app(app):
    app.cli.add_command(init_db_command)


