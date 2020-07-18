from flask import Flask, render_template, current_app
from os.path import isdir
from os import makedirs
import pymysql

from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)


with app.app_context():

    if not isdir(current_app.config['UPLOAD_FOLDER']):
        try:
            makedirs(current_app.config['UPLOAD_FOLDER'])
        except OSError:
            print('Failed to create upload directory')

    from . import db
    database = db.Database()
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import content
    app.register_blueprint(content.bp)

    try:
        if database.getSetting('configured'):
            app.config['SITENAME'] = database.getSetting('name')
            app.config['ALLOW_REGISTRATION'] = database.getSetting('registration')
            app.config['USE_REG_KEY'] = database.getSetting('use_key')

        else:
            app.config['SITENAME'] = 'Lucaflect Setup'
            app.config['ALLOW_REGISTRATION'] = True
            app.config['USE_REG_KEY'] = False

        app.config['LUCAFLECT_VERSION'] = 'Alpha 0'
    except pymysql.err.ProgrammingError:
        pass
