from flask import (Blueprint,  g, redirect, render_template, request, url_for, session)
from werkzeug.exceptions import abort
from . import db
import json
from re import sub

bp = Blueprint('content', __name__)
database=db.Database()

@bp.route('/new', methods=('GET', 'POST'))
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
            return render_template('message.html',message="Post '"+title+"' created!")
    return render_template('comic_editor.html')
