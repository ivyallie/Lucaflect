from flask import render_template, Blueprint, session, request, current_app, send_from_directory, g
from . import db
from . import auth
from json import loads, dumps
from os.path import join, basename
from werkzeug.security import generate_password_hash

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    #database = db.Database()
    comics=get_comics()
    '''
    comics_raw = database.query("SELECT * FROM comic;")
    comics=[]
    for comic in comics_raw:
        internal_title = comic['title'].replace("'", "")
        body_rawstr = comic['body']
        body=loads(body_rawstr)
        tags = body['tags']
        d = {
            'internal_title': comic['title'],
            'title': body['true_title'],
            'body': body['body_text'],
            'tags': tags
        }
        comics.append(d)
    '''
    return render_template('index.html', comics=comics)


@bp.route('/comic/<string:title>', methods=['GET'])
def get_single_comic(title):
    database = db.Database()
    comic = database.does_title_exist(title)

    def showTools():
        try:
            match = database.user_and_post_match(session['user_id'],comic['comic_id'])
        except KeyError:
            match = False
        return match or auth.is_admin()

    if comic:
        body = loads(comic['body'])

        images = []
        for image in body['imagelist']:
            src = image["file_path"]
            filename = basename(src)
            images.append(filename)

        internal_title = comic['title'].replace("'", "")
        author = database.query_user_id(comic['author_id'])
        author_name = author['full_name']
        show_tools = showTools()
        time = str(comic['posted'])
        content = {
            'internal_title': comic['title'],
            'comic_id': comic['comic_id'],
            'title': body['true_title'],
            'body': body['body_text'],
            'imagelist': images,
            'tags': body['tags'],
            'show_tools': show_tools,
            'author': author_name,
            'time': time,
            'format': body['format']
        }
    return render_template('single_comic.html', content=content)


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    print('Getting uploaded file...')
    #print(route)
    #return send_from_directory(current_app.config['UPLOAD_FOLDER'], route)
    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_dir, filename)

def get_comics(id="", howmany=0):
    database = db.Database()
    if id:
        query = '''SELECT * FROM comic WHERE author_id='''+str(id)+''' ORDER BY posted DESC;'''
    else:
        query = '''SELECT * FROM comic ORDER BY posted DESC;'''
    comics = database.query(query)
    processed_comics = []
    for comic in comics:
        internal_title = comic['title']
        body_rawstr = comic['body']
        body = loads(body_rawstr)
        tags = body['tags']
        author = database.query_user_id(comic['author_id'])
        d = {
            'comic_id': comic['comic_id'],
            'internal_title': internal_title,
            'title': body['true_title'],
            'body': body['body_text'],
            'tags': tags,
            'author': author['full_name']
        }
        processed_comics.append(d)
    return processed_comics

def load_weblinks(raw_links):
    for link in raw_links:
        url = str(link['link_url'])
        if not url.startswith('http://'):
            new_url = "http://" + url
            link['link_url'] = new_url
    return raw_links

@bp.route('/profile/<string:username>')
def user_profile(username):
    database = db.Database()
    user = database.query_user(username)

    if user:
        comics = get_comics(id=user['user_id'])
        try:
            meta = loads(user['meta'])
            web_links=load_weblinks(meta['web_links'])
        except TypeError:
            meta=""

        return render_template('user_profile.html', user=user, meta=meta, comics=comics, web_links=web_links)
    else:
        return render_template('404.html'), 404


@bp.route('/admin', methods=['GET', 'POST'])
@auth.login_required
def site_settings():
    if auth.is_admin():
        database = db.Database()
        if request.method == 'POST':
                print('Applying settings')
                if request.form['set_key']:
                    key=generate_password_hash(request.form['set_key'])
                else:
                    key="";
                form = {
                    'name': request.form['site_name'],
                    'description': request.form['site_description'],
                    'registration': request.form.get('allow_reg') != None,
                    'use_key': request.form.get('use_key') != None,
                    'key': key
                }
                for item in form.items():
                    name = item[0]
                    value = str(item[1])
                    if value:
                        if database.existSetting(name):
                            if len(value) > 20:
                                longvalue = dumps(value)
                                query = '''UPDATE lucaflect SET shortvalue=NULL, longvalue=%s WHERE name=%s'''
                                database.write(query, (longvalue, name))
                            else:
                                query = '''UPDATE lucaflect SET shortvalue=%s, longvalue=NULL WHERE name=%s'''
                                database.write(query, (value, name))
                    else:
                        print(name, 'is null!')
                current_app.config['SITENAME'] = database.getSetting('name')
                current_app.config['ALLOW_REGISTRATION'] = database.getSetting('registration')
                current_app.config['USE_REG_KEY'] = database.getSetting('use_key')


        settings = {
            'name': database.getSetting('name'),
            'registration': database.getSetting('registration'),
            'use_key': database.getSetting('use_key'),
            'description': database.getSetting('description')
        }
        return render_template('site_settings.html', settings=settings)
    else:
        return render_template('403.html'), 403

@bp.route('/admin/users', methods=['GET'])
@auth.login_required
def admin_users():
    if auth.is_admin():
        database = db.Database()
        query = '''SELECT * FROM user;'''
        users_raw = database.query(query)
        users = []
        for user in users_raw:
            u = {
                'username': user['username'],
                'full_name': user['full_name']
            }
            users.append(u)
        return render_template('admin_users.html',users=users)
    else:
        return render_template('403.html'), 403

@bp.route('/admin/comics', methods=['GET'])
@auth.login_required
def admin_comics():
    if auth.is_admin():
        comics=get_comics()
        return render_template('admin_comics.html', comics=comics)
    else:
        return render_template('403.html'), 403

@bp.route('/workspace')
@auth.login_required
def workspace():
    user=g.user
    comics = get_comics(id=user['user_id'])
    return render_template('workspace.html', comics=comics)

@bp.route('/contributors')
def contributors():
    database = db.Database()
    query = '''SELECT * FROM user;'''
    users_raw = database.query(query)
    users = []
    for user in users_raw:
        meta=auth.parse_user_meta(user)
        u = {
            'full_name': user['full_name'],
            'username': user['username'],
            'portrait': meta['portrait'],
            'bio': meta['bio'],
            'web_links': load_weblinks(meta['web_links'])
        }
        users.append(u)
    return render_template('contributors.html',users=users)


@bp.route('/beepers/')
def sql_test():

    beepers = database.query("""SELECT * FROM example;""")

    return render_template('sql_test.html', beepers=beepers)