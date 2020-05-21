from flask import Flask, render_template
import pymysql

from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

with app.app_context():
    from . import db
    database = db.Database()

    from . import routes
    app.register_blueprint(routes.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import content
    app.register_blueprint(content.bp)