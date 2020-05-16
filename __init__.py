from flask import Flask, render_template
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    from . import db

    @app.route('/beepers')
    def sql_test():
        sql_query = """SELECT * FROM example"""
        beepers = db.query(sql_query)
        for beeper in beepers:
            print(beeper)
        return render_template('sql_test.html', beepers=beepers)

    return app