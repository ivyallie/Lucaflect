from flask import render_template, Blueprint, session, url_for, jsonify, current_app, send_from_directory, redirect
from . import db
from json import loads
from os.path import join, basename

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    database = db.Database()
    comics_raw = database.query('''SELECT * FROM comic;''')
    comics=[]
    for comic in comics_raw:
        internal_title = comic['title'].replace("'", "")
        body_rawstr = comic['body']
        body=loads(body_rawstr)
        tags = body['tags']
        d = {
            'internal_title': internal_title,
            'title': body['true_title'],
            'body': body['body_text'],
            'tags': tags
        }
        comics.append(d)
    return render_template('index.html', comics=comics)


@bp.route('/comic/<string:title>', methods=['GET'])
def get_single_comic(title):
    database = db.Database()
    comic = database.does_title_exist(title)

    def showTools():
        try:
            return database.user_and_post_match(session['user_id'],comic['comic_id'])
        except KeyError:
            return False

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
            'internal_title': internal_title,
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




@bp.route('/beepers/')
def sql_test():

    beepers = database.query("""SELECT * FROM example;""")

    return render_template('sql_test.html', beepers=beepers)