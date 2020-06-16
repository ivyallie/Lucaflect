from flask import Blueprint, flash, g, redirect, request, render_template, current_app, session, url_for, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from . import routes
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
    database = db.Database()
    if current_app.config['ALLOW_REGISTRATION']:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            fullname = request.form['fullname']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif not fullname:
                error = 'Full name is required.'

            if current_app.config['USE_REG_KEY']:
                user_key = request.form['key']
                key_hash = database.getSetting('key')
                print(key_hash)

                if not check_password_hash(key_hash, user_key):
                    flash('You provided the incorrect signup key. Please double-check your invitation.', 'error')
                    error='Wrong key.'

            if error is None:
                user_query = '''SELECT * FROM user WHERE username="''' + username + '";'
                does_username_exist = database.query(user_query)
                if not does_username_exist:
                    database.write(
                        '''INSERT INTO user (username,password,full_name,join_date) VALUES (%s,%s,%s,CURRENT_DATE())''',
                        (username, generate_password_hash(password), fullname))
                    return render_template('message.html', message="Account created for "+username)
                else:
                    flash('The name ' + username + ' is already associated with an account.', 'error')

            print(error)

        return render_template('register.html')
    else:
        return render_template('403.html'), 403

@bp.route('/login', methods=('GET','POST'))
def login():
    database = db.Database()
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        error=None
        user=database.query_user(username)

        if not user:
            flash('There is no account registered to '+username, 'error')
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
            flash('Welcome, '+user['full_name']+'!','success')
            return redirect(url_for('routes.workspace'))

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
    flash('You have been successfully logged out.','success')
    return redirect(url_for('routes.index'))

@bp.route('/profile/<string:username>/edit', methods=['GET'])
@login_required
def edit_user(username):
    database = db.Database()
    affect_user = database.query_user(username)
    if g.user['user_group']=='admin' or g.user['user_id']==affect_user['user_id']:
        try:
            user_meta = loads(affect_user['meta'])
            bio = user_meta['bio']
            web_links = user_meta['web_links']
            portrait = user_meta['portrait']
        except TypeError:
            bio = ""
            web_links = ""
            portrait = False

        group = affect_user['user_group']

        return render_template('user_editor.html', user=affect_user, bio=bio, web_links=web_links, portrait=portrait, group=group)
    else:
        return render_template('403.html'), 403

def parse_user_meta(user):
    try:
        user_meta = loads(user['meta'])
        bio = user_meta['bio']
        web_links = user_meta['web_links']
        portrait = user_meta['portrait']
    except TypeError:
        bio=""
        web_links=""
        portrait=False

    meta = {
        'bio':bio,
        'web_links':web_links,
        'portrait':portrait
    }

    return meta

@bp.route('/update_user/<int:id>', methods=['POST'])
@login_required
def update_user(id):
    if g.user['user_id'] == id or g.user['user_group']=='admin':
        post=request.get_json()
        user = {
            'name': post['name'],
            'email': post['email'],
        }
        user_meta = {
            'bio': post['bio'],
            'web_links': post['web_links'],
            'portrait': post['portrait']
        }

        if post['group']:
            if g.user['user_group']=='admin' and g.user['user_id']!=id:
                group = post['group']

        user_meta_json = dumps(user_meta)

        if not group:
            query = '''UPDATE user SET full_name=%s, email=%s, meta=%s WHERE user_id="'''+str(id)+'''";'''
            database.write(query, (user['name'], user['email'], user_meta_json))
        else:
            query = '''UPDATE user SET full_name=%s, email=%s, user_group=%s, meta=%s  WHERE user_id="'''+str(id)+'''";'''
            database.write(query, (user['name'], user['email'], group, user_meta_json))
        response_text = jsonify('Modification successful')
        resp = make_response(response_text, 200)
        return resp
    else:
        return render_template('403.html')

@bp.route('/delete_user/<string:username>', methods=['GET','POST'])
@login_required
def delete_user(username):
    if is_admin():
        database = db.Database()
        user = database.query_user(username)
        user_id=user['user_id']
        meta=parse_user_meta(user)
        comics = routes.get_comics(user_id)
        if request.method=='POST':
            delete_comics = '''DELETE FROM comic WHERE author_id=%s;'''
            delete_user = '''DELETE FROM user WHERE user_id=%s;'''
            database.write(delete_comics,user_id)
            database.write(delete_user,user_id)
            flash('User '+username+" deleted.",'success')
            return redirect(url_for('routes.admin_users'))
        return render_template('delete_user_confirm.html',user=user, comics=comics, meta=meta)
    else:
        return render_template('403.html'), 403


def is_admin():
    user=g.user
    try:
        return user['user_group'] == 'admin'
    except TypeError:
        return False
