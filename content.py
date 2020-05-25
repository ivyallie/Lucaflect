from flask import (Blueprint,  g, redirect, render_template, request, url_for, session, flash, current_app)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
import json
from re import sub
from lucaflect.auth import login_required
from os.path import join, splitext, isdir
from os import makedirs
import datetime

bp = Blueprint('content', __name__)
database=db.Database()

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
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


@bp.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method=='POST':
        if request.files:
            files=[]
            upload_files = request.files.getlist("file")
            for file in upload_files:
                file_extension = splitext(file.filename)[1].lower()
                now = datetime.datetime.now()
                destination = join(current_app.config["UPLOAD_FOLDER"],str(now.year),str(now.month))
                filename = secure_filename(file.filename)
                if file_extension in current_app.config["IMGTYPES"]:
                    if validate_destination_dir(destination):
                        path=join(destination,filename)
                        file.save(path)
                        files.append(path)
                else:
                    print("Invalid filetype")
            print(files)
        return redirect(request.url)
    return render_template('upload_image.html')
