from flask import Blueprint, flash, g, redirect, request, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from . import db

database = db.Database()
bp = Blueprint('auth', __name__)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        error=None

        if not username:
            error='Username is required.'
        elif not password:
            error='Password is required.'
        elif not fullname:
            error='Full name is required.'

        if error is None:
            database.write('''INSERT INTO user (username,password,full_name,join_date) VALUES (%s,%s,%s,CURRENT_DATE())''',
            (username, generate_password_hash(password), fullname))
            print('Wrote new user')

        print(error)

    return render_template('register.html')
