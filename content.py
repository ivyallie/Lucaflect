from flask import (Blueprint,  g, redirect, render_template, request, url_for, session, flash, current_app, make_response, jsonify)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
from . import routes
from . import auth
import json
from re import sub
from lucaflect.auth import login_required, is_admin, is_authorized_to_edit, authorized
from os.path import join, splitext, isdir, isfile, split, dirname, abspath
from os import makedirs
import datetime
import time
from flask_dropzone import Dropzone
from urllib.parse import urlparse

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
        if database.user_and_post_match(user_id,comic_id) or is_admin():
            body = json.loads(comic['body'])
            content = {
                'id': comic['comic_id'],
                'title': body['true_title'],
                'body': body['body_text'],
                'imagelist': body['imagelist'],
                'tags': body['tags'],
                'format': body['format']
            }
            return render_template('comic_editor.html', title=title, content=content)
        else:
            return render_template('403.html'), 403
    else:
        return render_template('404.html'), 404

@bp.route('/collection/edit/<string:title>', methods=['GET'])
@login_required
def open_collection_editor(title):
    database = db.Database()
    collection = database.does_title_exist(title, table='collection')

    if collection:
        collection_id=collection['collection_id']
        user_id=session['user_id']
        if auth.authorized('collection',collection_id):
            internal_title = collection['title']
            meta = json.loads(collection['meta'])
            title = meta['title']
            description = meta['description']
            sequence_raw = json.loads(collection['members'])
            sequence = []
            for comic in sequence_raw:
                comic_data = database.does_title_exist(comic)
                if comic_data:
                    content = routes.get_comic_content(comic_data)
                    comic_listing = {
                        'internal_title': comic,
                        'title': content['title'],
                        'author': content['author'],
                    }
                    sequence.append(comic_listing)

            collection_id = collection['collection_id']

            content = {
                'collection_id':collection_id,
                'internal_title':internal_title,
                'title':title,
                'description':description,
                'sequence':json.dumps(sequence),
            }

            return render_template('collection_editor.html',content=content,authors=get_all_authors())
        else:
            return render_template('403.html'), 403
    else:
        return render_template('404.html'), 404




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
    user = g.user['full_name'].replace(" ", "").lower()
    unixtime = str(int(time.time()))
    new_filename = user+"_"+unixtime+"_"+filename
    return new_filename

def get_path(filename):
    APP_ROOT = dirname(abspath(__file__))
    path = join(APP_ROOT, current_app.config['UPLOAD_FOLDER'], filename)
    return path

def get_unique_title(user_title, table='comic'):
    title_stripped = sub('[^A-Za-z0-9 ]+', '', user_title)
    title = sub(' ', '_', title_stripped)
    if not database.does_title_exist(title,table):
        print('Title is unique.')
        return title
    else:
        print('Title must be numbered')
        title_blocked = True
        number = 1
        while title_blocked:
            title_with_number = title+"_"+str(number)
            if database.does_title_exist(title_with_number,table):
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
        internal_filename = get_unique_filename(securename)
        path = get_path(internal_filename)
        f.save(path)
        response_data = jsonify({'path': path, 'filename': f.filename, 'internal_filename': internal_filename})
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
    clean_title = get_unique_title(title)
    user_id = session['user_id']
    post_json = process_post_content(post)
    to_write = '''INSERT INTO comic (author_id,title,body,posted) VALUES (%s, %s, %s, CURRENT_TIMESTAMP())'''
    database.write(to_write, (user_id, clean_title, post_json))
    response_text = jsonify({'redirect': url_for('content.open_comic_editor', title=clean_title)})
    resp = make_response(response_text, 200)
    flash('"'+title+'" posted!','success')
    return resp

@bp.route('/modify_comic/<int:id>', methods=['POST'])
@login_required
def modify_comic(id):
    post = request.get_json()
    post_json = process_post_content(post)
    if database.user_and_post_match(session['user_id'],id) or is_admin():
        #print(post_json)
        modification = '''UPDATE comic SET body=%s WHERE comic_id=%s'''
        database.write(modification, (post_json, id))
        response_text = jsonify('Modification successful')
        resp = make_response(response_text, 200)
    else:
        response_text = jsonify('You are not authorized to modify this post.')
        resp = make_response(response_text, 403)
    return resp

@bp.route('/collection/post', methods=['POST'])
@login_required
def post_collection():
    post=request.get_json()
    title=post['title']
    user_id = session['user_id']
    try:
        collection_id = int(post['id'])
    except TypeError:
        collection_id=False
    meta = {
        'title':title,
        'description':post['description']
    }
    sequence = post['sequence']
    meta_json = json.dumps(meta)
    sequence_json = json.dumps(sequence)
    if collection_id:
        print('updating',title)
        if auth.authorized('collection', collection_id):
            to_write = '''UPDATE collection SET meta=%s, members=%s WHERE collection_id=%s;'''
            record_query = '''SELECT * FROM collection WHERE collection_id=%s;'''
            record = database.query(record_query,values=collection_id,fetchone=True)
            return_title=record['title']
            database.write(to_write,(meta_json,sequence_json,collection_id))
            flash('Successfully modified collection "'+title+'"!', 'success')
        else:
            return render_template('403.html'),403
    else:
        print('creating new',title)
        clean_title = get_unique_title(title, table='collection')
        return_title = clean_title
        to_write = '''INSERT INTO collection (author_id,posted,title,meta,members) VALUES (%s,CURRENT_TIMESTAMP(),%s,%s,%s);'''
        database.write(to_write,(user_id,clean_title,meta_json,sequence_json))
        flash('Collection "'+title+'" created successfully!','success')
    response_text = jsonify({'redirect': url_for('content.open_collection_editor', title=return_title)})
    resp = make_response(response_text, 200)
    return resp


@bp.route('/delete/<string:title>', methods=['GET', 'POST'])
@login_required
def delete_comic(title):
    database = db.Database()
    comic = database.does_title_exist(title)
    id = comic['comic_id']
    if request.method=='GET':
        request_url=urlparse(request.referrer).path
        session['delete_redirect'] = request_url
        if session.get('delete_redirect') == url_for('routes.get_single_comic', title=title):
            session['delete_redirect'] = url_for('routes.workspace')
    if database.user_and_post_match(session['user_id'], id) or is_admin():
        comic_body = json.loads(comic['body'])
        display_title = comic_body['true_title']
        if request.method == 'POST':
            database.delete_comic(id)
            flash('"'+display_title+'" deleted.','success')
            return redirect(session.get('delete_redirect'))

        return render_template('delete_confirm.html', title=title, display_title=display_title, refer_url=request.referrer)
    else:
        return render_template('403.html')

@bp.route('/collection/new', methods=['GET'])
@login_required
def new_collection():
    return render_template('collection_editor.html', authors=get_all_authors())

def get_all_authors():
    database = db.Database()
    authors_query = '''SELECT * FROM user;'''
    authors = database.query(authors_query)
    return authors

