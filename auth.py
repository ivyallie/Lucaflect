from flask import Blueprint, flash, g, redirect, request, render_template, current_app, session, url_for, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
import functools
from json import dumps, loads

database = db.Database()
bp = Blueprint('auth', __name__)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view


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
                    return render_template('message.html', message="Account created for "+username)
                else:
                    flash('The email you provided, ' + username + ', is already associated with an account.', 'error')

            print(error)

        return render_template('register.html')
    else:
        return render_template('403.html'), 403

@bp.route('/login', methods=('GET','POST'))
def login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        error=None
        user=database.query_user(email)

        if not user:
            flash('There is no account registered to '+email, 'error')
            error='NoUser'
        elif not check_password_hash(user['password'], password):
            flash('Invalid password.', 'error')
            error='BadPassword'

        if error is None:
            session.clear()
            session['user'] = user
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            load_logged_in_user()
            return render_template('message.html', message='Welcome, '+user['full_name']+'! You are now logged in.')

    return render_template('login.html')



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = session['user']

@bp.route('/logout')
def logout():
    session.clear()
    load_logged_in_user()
    return render_template('message.html', message='You have been successfully logged out.')

@bp.route('/edit_profile', methods=['GET'])
@login_required
def edit_logged_in_user():
    user = database.query_user_id(g.user['user_id'])
    user_meta = loads(user['meta'])
    bio = user_meta['bio']
    web_links = user_meta['web_links']
    portrait = user_meta['portrait']

    if request.method=='POST':
        email = request.form['email']
        name = request.form['name']
        query = '''UPDATE user SET full_name = %s WHERE user_id='''+str(g.user['user_id'])+";"
        database.write(query,name)
        return render_template('message.html', message="Your profile has been amended.")

    return render_template('user_editor.html', user=user, bio=bio, web_links=web_links, portrait=portrait)

@bp.route('/update_user/<int:id>', methods=['POST'])
@login_required
def update_user(id):
    if g.user['user_id'] == id:
        post=request.get_json()
        user = {
            'name': post['name'],
            'email': post['email'],

        }
        print(user['name'])
        print(user['email'])
        user_meta = {
            'bio': post['bio'],
            'web_links': post['web_links'],
            'portrait': post['portrait']
        }
        user_meta_json = dumps(user_meta)
        query = '''UPDATE user SET full_name=%s, email=%s, meta=%s WHERE user_id="'''+str(id)+'''";'''
        database.write(query, (user['name'], user['email'], user_meta_json))
        response_text = jsonify('Modification successful')
        resp = make_response(response_text, 200)
        return resp
    else:
        return render_template('403.html')


def check_admin():
    try:
        user_id = g.user['user_id']
    except TypeError:
        return False
    user_record = database.query_user_id(user_id)
    return user_record['group'] == 'admin'
