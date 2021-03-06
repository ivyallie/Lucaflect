from flask import (Blueprint,  g, redirect, render_template, request, url_for, session, flash, current_app, make_response, jsonify)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
from . import routes
from . import auth
import json
from re import sub
from lucaflect.auth import login_required, is_admin, authorized
from os.path import join, splitext, isdir, isfile, split, dirname, abspath
from os import makedirs
import datetime
import time
#from flask_dropzone import Dropzone
from urllib.parse import urlparse


if current_app.config['SCHEME']=='gcloud':
    from . import gcloud
    bucket = current_app.config['UPLOAD_FOLDER']

bp = Blueprint('content', __name__)
database=db.Database()
#dropzone=Dropzone(current_app)

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    database = db.Database()
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
    database = db.Database()
    comic = database.does_title_exist(title)

    if auth.is_admin():
        admin=True
    else:
        admin=False

    if comic:
        comic_id = comic['comic_id']
        user_id = session['user_id']
        draft = comic['draft']
        if draft:
            flash('This comic is still in editorial queue. It will be visible on the site when an editor approves it.')
        if auth.authorized('comic',comic_id):
            body = json.loads(comic['body'])
            try:
                preview_image=body['preview_image']
            except KeyError:
                preview_image=''
            content = {
                'id': comic['comic_id'],
                'title': body['true_title'],
                'body': body['body_text'],
                'imagelist': body['imagelist'],
                'tags': body['tags'],
                'format': body['format'],
                'preview_image': preview_image,
                'draft': draft
            }
            return render_template('comic_editor.html', title=title, content=content, admin=admin)
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


@bp.route('/admin/homepage', methods=['GET'])
@auth.login_required
def admin_homepage():
    database = db.Database();
    if database.existSetting('homepage_sequence'):
        sequence = database.getSetting('homepage_sequence')
    else:
        default_sequence = [{'type':'smartlist', 'title': 'Recent comics', 'how_many': 10, 'internal_title': 'recent_comics'}]
        sequence = json.dumps(default_sequence)
    return render_template('homepage_editor.html', authors=get_all_authors(), sequence=sequence)

@bp.route('/admin/homepage/modify', methods=['POST'])
@auth.login_required
def update_homepage():
    print('Updating homepage!')
    if auth.is_admin():
        database = db.Database()
        if request.method == 'POST':
            sequence = request.get_json()
            sequence_json = json.dumps(sequence)
            if database.existSetting('homepage_sequence'):
                query = '''UPDATE lucaflect SET shortvalue=NULL, longvalue=%s WHERE name=%s'''
                database.write(query, (sequence_json,'homepage_sequence'))
                flash('Homepage sequence updated.','success')
            response_text = json.dumps({'message':'success','status':'ok'})
            resp = make_response(response_text, 200)
            return resp

    else:
        return render_template('403.html'), 403

def validate_destination_dir(path):
    if isdir(path):
        return path
    else:
        makedirs(path)
        return path


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
    database=db.Database()
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
        if current_app.config['SCHEME']=='gcloud':
            gcloud.gcloud_upload(bucket,f,internal_filename)
            path = url_for('routes.uploaded_file', filename=internal_filename)
        else:
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
        'format': post['format'],
        'preview_image': post['preview_image']
    }
    return json.dumps(post_content)

@bp.route('/post_comic', methods=['POST'])
@login_required
def post_comic():
    database=db.Database()
    post = request.get_json()
    title = post['title']
    clean_title = get_unique_title(title)
    user_id = session['user_id']
    post_json = process_post_content(post)
    to_write = '''INSERT INTO comic (author_id,title,body,posted,draft) VALUES (%s, %s, %s, CURRENT_TIMESTAMP(),1)'''
    database.write(to_write, (user_id, clean_title, post_json))
    response_text = jsonify({'redirect': url_for('content.open_comic_editor', title=clean_title)})
    resp = make_response(response_text, 200)
    flash('"'+title+'" submitted to editorial queue.','success')
    return resp

@bp.route('/modify_comic/<int:id>', methods=['POST'])
@login_required
def modify_comic(id):
    post = request.get_json()
    title = post['title']
    post_json = process_post_content(post)
    if auth.authorized('comic',id):
        database=db.Database()
        #print(post_json)
        modification = '''UPDATE comic SET body=%s WHERE comic_id=%s'''
        database.write(modification, (post_json, id))
        record_query = '''SELECT * FROM comic WHERE comic_id=%s;'''
        record = database.query(record_query, values=id, fetchone=True)
        return_title = record['title']
        response_text = jsonify({'redirect': url_for('content.open_comic_editor', title=return_title)})
        flash('"' + title + '" modified successfully', 'success')
        resp = make_response(response_text, 200)
    else:
        response_text = jsonify('You are not authorized to modify this post.')
        resp = make_response(response_text, 403)
    return resp

@bp.route('/collection/post', methods=['POST'])
@login_required
def post_collection():
    database = db.Database()
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
    print(collection_id)
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

    redirect_url = url_for('content.open_collection_editor', title=return_title)
    response_text = jsonify({'redirect': redirect_url})
    resp = make_response(response_text, 200)
    return resp

@bp.route('/approve/<string:title>', methods=['GET'])
@login_required
def approve_comic(title):
    set_draft_status(title,0)
    flash(title+' approved!','success')
    return redirect(request.referrer)

@bp.route('/retract/<string:title>', methods=['GET'])
@login_required
def retract_comic(title):
    set_draft_status(title,1)
    flash(title+' retracted.', 'success')
    return redirect(request.referrer)


def set_draft_status(title, value):
    database = db.Database()
    comic = database.does_title_exist(title)
    id = comic['comic_id']
    if auth.is_admin():
        query = '''UPDATE comic SET draft=%s WHERE comic_id=%s;'''
        database.write(query,(str(value),str(id)))
    else:
        return render_template('403.html'),403


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
    if auth.authorized('comic',id):
        comic_body = json.loads(comic['body'])
        display_title = comic_body['true_title']
        if request.method == 'POST':
            database.delete_comic(id)
            flash('"'+display_title+'" deleted.','success')
            return redirect(session.get('delete_redirect'))

        return render_template('delete_confirm.html', title=title, display_title=display_title, refer_url=request.referrer)
    else:
        return render_template('403.html'),403

@bp.route('/collection/delete/<string:title>',methods=['GET','POST'])
@login_required
def delete_collection(title):
    database=db.Database()
    collection=database.does_title_exist(title,table='collection')
    id = collection['collection_id']
    if request.method=='GET':
        request_url=urlparse(request.referrer).path
        session['delete_redirect'] = request_url
        if session.get('delete_redirect') == url_for('routes.display_collection', title=title):
            session['delete_redirect'] = url_for('routes.workspace')
    if auth.authorized('collection',id):
        meta = json.loads(collection['meta'])
        display_title = meta['title']
        if request.method == 'POST':
            database.delete_collection(id)
            flash('"'+display_title+'" deleted.','success')
            return redirect(session.get('delete_redirect'))
        return render_template('delete_confirm.html', title=title, display_title=display_title, refer_url=request.referrer)
    else:
        return render_template('403.html'),403

@bp.route('/collection/new', methods=['GET'])
@login_required
def new_collection():
    return render_template('collection_editor.html', authors=get_all_authors())

def get_all_authors():
    database = db.Database()
    authors_query = '''SELECT * FROM user;'''
    authors = database.query(authors_query)
    return authors

