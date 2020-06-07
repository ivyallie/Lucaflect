from flask import (Blueprint,  g, redirect, render_template, request, url_for, session, flash, current_app, make_response, jsonify)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
from . import routes
import json
from re import sub
from lucaflect.auth import login_required
from os.path import join, splitext, isdir, isfile, split, dirname, abspath
from os import makedirs
import datetime
import time
from flask_dropzone import Dropzone

bp = Blueprint('content', __name__)
database=db.Database()
dropzone=Dropzone(current_app)

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    if 'uploaded_images' not in session:
        session['uploaded_images'] = []

    if request.method == 'POST':
        title=request.form['title']
        body=request.form['body']
        tags=request.form['tags']
        error=None

        def process_tags(input_string):
            return input_string.split(",")

        def make_json(body,tags,title):
            tags=process_tags(tags)
            post_content= {
                "true_title": title,
                "body_text": body,
                "tags": tags
            }
            json_obj = json.dumps(post_content)
            return json_obj


        if error is not None:
            flash(error)
        else:
            json_obj = make_json(body,tags,title)
            clean_title = sub('[^A-Za-z0-9 ]+', '', title)
            user_id=session['user_id']
            to_write='''INSERT INTO comic (author_id,title,body,posted) VALUES (%s, QUOTE(%s), %s, CURRENT_TIMESTAMP())'''
            database.write(to_write,(user_id,clean_title,json_obj))
            return render_template('message.html', message="Post '"+title+"' created!")

    return render_template('comic_editor.html')

@bp.route('/edit/<string:title>', methods=['GET'])
@login_required
def open_comic_editor(title):
    comic = database.does_title_exist(title)

    if comic:
        comic_id = comic['comic_id']
        user_id = session['user_id']
        if database.user_and_post_match(user_id,comic_id):
            body = json.loads(comic['body'])
            content = {
                'id': comic['comic_id'],
                'title': body['true_title'],
                'body': body['body_text'],
                'imagelist': body['imagelist'],
                'tags': body['tags'],
                'format': body['format']
            }
            return render_template('comic_editor.html', content=content)
        else:
            return render_template('403.html'), 403
    else:
        return render_template('404.html'), 4040




def validate_destination_dir(path):
    if isdir(path):
        print('Path Exists')
        return path
    else:
        print('Path exists not.')
        makedirs(path)
        return path
        '''
        try:
            makedirs(path)
            return path
        except OSError:
            print('OSError occurred!')
            return False
        '''


def get_unique_filename(filename):
    APP_ROOT = dirname(abspath(__file__))
    now = datetime.datetime.now()
    user = g.user['full_name'].replace(" ", "").lower()
    #main_path = join(current_app.config["UPLOAD_FOLDER"], user, str(now.year)+"_"+str(now.month))
    unixtime = str(int(time.time()))
    new_filename = user+"_"+unixtime+"_"+filename
    path = join(APP_ROOT,current_app.config['UPLOAD_FOLDER'],new_filename)
    #full_path=join(main_path, new_filename)
    #validate_destination_dir(main_path)
    return path

def get_unique_title(user_title):
    title_stripped = sub('[^A-Za-z0-9 ]+', '', user_title)
    title = sub(' ', '_', title_stripped)
    if not database.does_title_exist(title):
        print('Title is unique.')
        return title
    else:
        print('Title must be numbered')
        title_blocked = True
        number = 1
        while title_blocked:
            title_with_number = title+"_"+str(number)
            if database.does_title_exist(title_with_number):
                number += 1
            else:
                return title_with_number


@bp.route('/upload', methods=['PUT'])
@login_required
def upload():
    # This is the saint whose technique I finally got to work: https://github.com/ibrahimokdadov/upload_file_python/blob/master/src/app_display_image.py
    f = request.files['file']
    file_extension = splitext(f.filename)[1].lower()
    if file_extension in current_app.config["IMGTYPES"]:
        securename = secure_filename(f.filename)
        path = get_unique_filename(securename)
        f.save(path)
        response_data = jsonify({'path': path, 'filename': f.filename})
        resp = make_response(response_data, 201)
    else:
        fail_response = jsonify('Unsupported filetype.')
        resp = make_response(fail_response, 415)
    return resp

def process_post_content(post):
    post_content = {
        'true_title': post['title'],
        'body_text': post['body_text'],
        'tags': post['tags'],
        'imagelist': post['image_list'],
        'format': post['format']
    }
    return json.dumps(post_content)

@bp.route('/post_comic', methods=['POST'])
@login_required
def post_comic():
    post = request.get_json()
    title = post['title']
    #print('Format:', post['format']),
    clean_title = get_unique_title(title)
    user_id = session['user_id']
    post_json = process_post_content(post)
    to_write = '''INSERT INTO comic (author_id,title,body,posted) VALUES (%s, QUOTE(%s), %s, CURRENT_TIMESTAMP())'''
    database.write(to_write, (user_id, clean_title, post_json))
    response_text = jsonify({'redirect': url_for('content.open_comic_editor', title=clean_title)})
    resp = make_response(response_text, 200)
    return resp

@bp.route('/modify_comic/<int:id>', methods=['POST'])
@login_required
def modify_comic(id):
    print('Modify comic!')
    post = request.get_json()
    post_json = process_post_content(post)
    if database.user_and_post_match(session['user_id'],id):
        #print(post_json)
        modification = '''UPDATE comic SET body=%s WHERE comic_id=%s'''
        database.write(modification, (post_json, id))
        response_text = jsonify('Modification successful')
        resp = make_response(response_text, 200)
    else:
        response_text = jsonify('You are not authorized to modify this post.')
        resp = make_response(response_text, 403)
    return resp

