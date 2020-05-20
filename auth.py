from flask import Blueprint, flash, g, redirect, request, render_template, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from . import db

database = db.Database()
bp = Blueprint('auth', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if current_app.config['ALLOW_REGISTRATION']:
        if request.method == 'POST':
            username = request.form['email']
            password = request.form['password']
            fullname = request.form['fullname']
            error = None

            if not username:
                error = 'Email is required.'
            elif not password:
                error = 'Password is required.'
            elif not fullname:
                error = 'Full name is required.'

            if current_app.config['REGISTRATION_KEY']:
                key = request.form['key']
                if key != current_app.config['REGISTRATION_KEY']:
                    flash('You provided the incorrect signup key. Please double-check your invitation.', 'error')

            if error is None:
                user_query = '''SELECT * FROM user WHERE username="''' + username + '";'
                does_username_exist = database.query(user_query)
                if not does_username_exist:
                    database.write(
                        '''INSERT INTO user (username,password,full_name,join_date) VALUES (%s,%s,%s,CURRENT_DATE())''',
                        (username, generate_password_hash(password), fullname))
                    print('Wrote new user')
                else:
                    flash('The email you provided, ' + username + ', is already associated with an account.', 'error')

            print(error)

        return render_template('register.html')
    else:
        return render_template('403.html'), 403


