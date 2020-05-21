from flask import render_template, Blueprint
from . import db
from json import loads

bp = Blueprint('routes', __name__)

database = db.Database()

@bp.route('/')
def index():
    comics_raw = database.query("""SELECT * FROM comic;""")
    print(comics_raw)
    comics=[]
    for comic in comics_raw:
        body_raw=str(comic['body']).replace('\'', '\"')
        body=loads(body_raw)
        tags = body['tags']
        d = {
            'title':comic['title'],
            'body':body['body_text'],
            'tags':tags
        }
        comics.append(d)
    return render_template('index.html', comics=comics)


@bp.route('/beepers/')
def sql_test():

    beepers = database.query("""SELECT * FROM example;""")

    return render_template('sql_test.html', beepers=beepers)