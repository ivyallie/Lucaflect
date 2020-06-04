from flask import (Blueprint,  g, redirect, render_template, request, url_for, session, flash, current_app, make_response, jsonify)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
import json
from re import sub
from lucaflect.auth import login_required
from os.path import join, splitext, isdir, isfile, split
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


def validate_destination_dir(path):
    if isdir(path):
        return path
    else:
        try:
            makedirs(path)
        except OSError:
            return False


def get_unique_filename(filename):
    now = datetime.datetime.now()
    user = g.user['full_name'].replace(" ", "").lower()
    main_path = join(current_app.config["UPLOAD_FOLDER"], user, str(now.year)+"_"+str(now.month))
    unixtime = str(int(time.time()))
    new_filename = user+"_"+unixtime+"_"+filename
    full_path=join(main_path, new_filename)
    validate_destination_dir(main_path)
    return full_path


@bp.route('/upload', methods=['PUT'])
@login_required
def upload():
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