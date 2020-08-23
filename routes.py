from flask import send_file, render_template, Blueprint, session, request, current_app, send_from_directory, g, make_response, jsonify, flash
from . import db
from . import auth
from .common import reformat_timestamp, year
from json import loads, dumps
from os.path import basename
from werkzeug.security import generate_password_hash
import tempfile

if current_app.config['SCHEME']=='gcloud':
    from . import gcloud
    bucket = current_app.config['UPLOAD_FOLDER']

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    comics=assembleHomepage()
    return render_template('index.html', comics=comics)

def assembleHomepage():
    database = db.Database()
    homepage_content=[]
    default_sequence = [{'type':'smartlist', 'title': 'Recent comics', 'how_many': 10, 'internal_title': 'recent_comics'}]
    if database.existSetting('homepage_sequence'):
        sequence = database.getSetting('homepage_sequence')
        if not sequence:
            sequence = default_sequence
    else:
        #default sequence
        sequence = default_sequence
    recentComics = get_comics()
    recentCollections = get_collections()

    comic_index = 0
    collection_index = 0

    if sequence:
        for item in sequence:
            if item['type']=='comic':
                comic = database.does_title_exist(item['internal_title'])
                comic_content = get_comic_content(comic)
                homepage_content.append(comic_content)
            elif item['type']=='collection':
                collection = getCollection(item['internal_title'])
                if item['expand'] != "0":
                    collection_sequence = collection['sequence']
                    for c in collection_sequence:
                        comic = database.does_title_exist(c['internal_title'])
                        comic_content=get_comic_content(comic)
                        homepage_content.append(comic_content)
                else:
                    collection_listing = unexpandedCollectionListing(collection)
                    homepage_content.append(collection_listing)
            elif item['type']=='smart':
                if database.existSetting('description'):
                    description=database.getSetting('description')
                else:
                    description='No description set. Write a description in Site Admin.'
                listing = {
                    'type': 'textblock',
                    'title': item['title'],
                    'body': description
                }
                homepage_content.append(listing)
            elif item['type']=='smartlist':
                if item['internal_title']=='recent_collections':
                    how_many = int(item['how_many'])
                    i = 0
                    while i < how_many+1:
                        try:
                            collection_listing = unexpandedCollectionListing(recentCollections[collection_index])
                            collection_index += 1
                            i += 1
                            homepage_content.append(collection_listing)
                        except IndexError:
                            break
                else:
                    how_many = int(item['how_many'])
                    i = 0
                    while i < how_many+1:
                        try:
                            comic=recentComics[comic_index]
                            comic_index += 1
                            i += 1
                            homepage_content.append(comic)
                        except IndexError:
                            break
    else:
        listing = {
            'type': 'textblock',
            'title': 'No comics?!',
            'body': 'Once there are comics in the database, you\'ll see them here!'
        }
        homepage_content.append(listing)
    return homepage_content


def unexpandedCollectionListing(collection):
    database = db.Database()
    sequence = collection['sequence']

    #build montage
    previews = []
    for c in sequence:
        comic = database.does_title_exist(c['internal_title'])
        comic_content = get_comic_content(comic)
        previews.append(comic_content['preview_image'])
    montage = []
    slot=0

    while slot<3:
        if slot<len(previews):
            if previews[slot]!='':
                montage.append(previews[slot])
                slot+=1
            else:
                slot+=1
        else:
            print('need placeholder')
            montage.append('')
            slot+=1

    return {'internal_title': collection['internal_title'],
            'title': collection['title'],
            'body': collection['description'],
            'type': 'collection',
            'montage': montage}

@bp.route('/about/', methods=['GET'])
def about():
    database=db.Database()

    if database.existSetting('description'):
        description = database.getSetting('description')
    else:
        description = 'No description set. Write a description in Site Admin.'

    return render_template('about.html',description=description)


@bp.route('/comic/<string:title>', methods=['GET'])
def get_single_comic(title):
    database = db.Database()
    comic = database.does_title_exist(title)

    if comic:
        content = get_comic_content(comic)
        content['show_tools']=auth.authorized('comic',comic['comic_id'])

        author=False

        if database.getSetting('mini_profile'):
            user = database.query_user(content['author_username'])
            meta = auth.parse_user_meta(user)
            author = {
                'full_name': user['full_name'],
                'username': user['username'],
                'portrait': meta['portrait'],
                'bio': meta['bio'],
                'web_links': load_weblinks(meta['web_links'])
            }


        return render_template('single_comic.html', content=content, user=author)

    else:
        return render_template('404.html'),404

def get_comic_content(comic):
    database = db.Database()

    body = loads(comic['body'])

    images = []
    for image in body['imagelist']:
        src = image["file_path"]
        filename = basename(src)
        images.append(filename)

    internal_title = comic['title'].replace("'", "")
    author = database.query_user_id(comic['author_id'])
    author_name = author['full_name']
    author_username = author['username']
    time = str(comic['posted'])
    try:
        preview_image = body['preview_image']
    except KeyError:
        #print('No preview image, defaulting.')
        preview_image = ''
    content = {
        'internal_title': comic['title'],
        'comic_id': comic['comic_id'],
        'title': body['true_title'],
        'body': body['body_text'],
        'imagelist': images,
        'tags': body['tags'],
        'author': author_name,
        'author_username': author_username,
        'time': reformat_timestamp(time),
        'year': year(time),
        'format': body['format'],
        'preview_image':preview_image
    }
    return content

@bp.route('/collection/<string:title>', methods=['GET'])
def display_collection(title):
    collection_data=getCollection(title)
    return render_template('collection.html',collection=collection_data)

def getCollection(title):
    database = db.Database()
    collection = database.does_title_exist(title, table='collection')
    if collection:
        meta = loads(collection['meta'])
        author = database.query_user_id(collection['author_id'])
        author_name = author['full_name']
        sequence_dictionary = loads(collection['members'])
        sequence = buildCollectionSequence(sequence_dictionary)

        collection_data = {
            'title': meta['title'],
            'internal_title': title,
            'description': meta['description'],
            'sequence': sequence,
            'author': author_name,
            'author_username': author['username'],
            'time': reformat_timestamp(str(collection['posted'])),
            'show_tools': auth.authorized('collection', collection['collection_id'])
        }
        return collection_data


def buildCollectionSequence(sequence_dictionary):
    database=db.Database()
    sequence=[]
    for c in sequence_dictionary:
        comic = database.does_title_exist(c)
        if comic:
            content = get_comic_content(comic)
            comic_listing = {
                'internal_title': c,
                'title': content['title'],
                'author': content['author'],
                'preview_image': content['preview_image']
            }
            sequence.append(comic_listing)
    return sequence


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    if current_app.config['SCHEME']=='gcloud':
        return gcloud.gcloud_retrieve(bucket,filename,filename)
    else:
        upload_dir = current_app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_dir, filename)



@bp.route('/getcomics/<int:id>', methods=['GET'])
def get_comics_for_js(id):
    comics=get_comics(id)
    response_data = {
        'comics':comics,
    }
    resp = make_response(jsonify(response_data),200)

    return resp

@bp.route('/getcollections/', methods=['GET'])
def get_collections_for_js():
    collections=get_collections()
    response_data = {
        'collections':collections,
    }
    resp = make_response(jsonify(response_data),200)
    return resp

def get_comics(id="", howmany=0, show=''):
    database = db.Database()
    if show in ['drafts','all']:

        if show == 'drafts':

            if id:
                query = '''SELECT * FROM comic WHERE author_id=%s AND draft=1 ORDER BY posted DESC;'''
                comics = database.query(query, (str(id)))
            else:
                query = '''SELECT * FROM comic WHERE draft=1 ORDER BY posted DESC;'''
                comics = database.query(query)
        else:

            if id:
                query = '''SELECT * FROM comic WHERE author_id=%s ORDER BY posted DESC;'''
                comics = database.query(query,(str(id)))
            else:
                query = '''SELECT * FROM comic ORDER BY posted DESC;'''
                comics = database.query(query)

    else:

        if id:
            query = '''SELECT * FROM comic WHERE author_id=%s AND draft=0 ORDER BY posted DESC;'''
            comics = database.query(query,(str(id)))
        else:
            query = '''SELECT * FROM comic WHERE draft=0 ORDER BY posted DESC;'''
            comics = database.query(query)

    processed_comics = []
    for comic in comics:
        internal_title = comic['title']
        body_rawstr = comic['body']
        body = loads(body_rawstr)
        tags = body['tags']
        author = database.query_user_id(comic['author_id'])
        try:
            preview_image = body['preview_image']
        except KeyError:
            preview_image = ''
        d = {
            'comic_id': comic['comic_id'],
            'time': reformat_timestamp(str(comic['posted'])),
            'internal_title': internal_title,
            'title': body['true_title'],
            'body': body['body_text'],
            'tags': tags,
            'author': author['full_name'],
            'preview_image': preview_image,
            'draft': comic['draft']
        }
        processed_comics.append(d)
    return processed_comics


def get_collections(id="",howmany=0):
    database=db.Database()
    if id:
        query = '''SELECT * FROM collection WHERE author_id=%s ORDER BY posted DESC;'''
        collections = database.query(query,values=id)
    else:
        query = '''SELECT * FROM collection ORDER BY posted DESC;'''
        collections = database.query(query)
    processed = []
    for collection in collections:
        internal_title = collection['title']
        meta_raw = collection['meta']
        meta = loads(meta_raw)
        author = database.query_user_id(collection['author_id'])
        d = {
            'collection_id': collection['collection_id'],
            'internal_title': internal_title,
            'title': meta['title'],
            'description': meta['description'],
            'author': author['full_name'],
            'time': reformat_timestamp(str(collection['posted']))
        }
        processed.append(d)
    return processed

def load_weblinks(raw_links):
    for link in raw_links:
        url = str(link['link_url'])
        if not (url.startswith('http://') or url.startswith('https://')):
            new_url = "http://" + url
            link['link_url'] = new_url
    return raw_links

@bp.route('/profile/<string:username>')
def user_profile(username):
    database = db.Database()
    user = database.query_user(username)

    if user:
        comics = get_comics(id=user['user_id'])
        collections = get_collections(id=user['user_id'])
        try:
            meta = loads(user['meta'])
            web_links=load_weblinks(meta['web_links'])
        except TypeError:
            web_links=""
            meta=""

        return render_template('user_profile.html', user=user, meta=meta, comics=comics, collections=collections, web_links=web_links)
    else:
        return render_template('404.html'), 404


@bp.route('/admin', methods=['GET', 'POST'])
@auth.login_required
def site_settings():
    if auth.is_admin():
        database = db.Database()
        if request.method == 'POST':
                if request.form['set_key']:
                    key=generate_password_hash(request.form['set_key'])
                else:
                    key=""
                form = {
                    'name': request.form['site_name'],
                    'description': request.form['site_description'],
                    'registration': request.form.get('allow_reg') != None,
                    'use_key': request.form.get('use_key') != None,
                    'key': key,
                    'mini_profile': request.form.get('show_mini_profile') != None,
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
                current_app.config['SITENAME'] = database.getSetting('name')
                current_app.config['ALLOW_REGISTRATION'] = database.getSetting('registration')
                current_app.config['USE_REG_KEY'] = database.getSetting('use_key')
                flash('Site settings changed.','success')


        settings = {
            'name': database.getSetting('name'),
            'registration': database.getSetting('registration'),
            'use_key': database.getSetting('use_key'),
            'description': database.getSetting('description'),
            'mini_profile': database.getSetting('mini_profile')
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
            you = (user == session['user'])
            u = {
                'username': user['username'],
                'full_name': user['full_name'],
                'group': user['user_group'],
                'you': you
            }
            users.append(u)
        return render_template('admin_users.html',users=users)
    else:
        return render_template('403.html'), 403

@bp.route('/admin/comics', methods=['GET'])
@auth.login_required
def admin_comics():
    if auth.is_admin():
        comics=get_comics(show='all')
        return render_template('admin_comics.html', comics=comics)
    else:
        return render_template('403.html'), 403

@bp.route('/admin/queue', methods=['GET'])
@auth.login_required
def editorial_queue():
    if auth.is_admin():
        comics=get_comics(show='drafts')
        return  render_template('editor_queue.html', comics=comics)
    else:
        return render_template('403.html'), 403


@bp.route('/admin/collections', methods=['GET'])
@auth.login_required
def admin_collections():
    if auth.is_admin():
        collections=get_collections()
        return render_template('admin_collections.html',collections=collections)
    else:
        return render_template('403.html'), 403


@bp.route('/workspace')
@auth.login_required
def workspace():
    user=g.user
    comics = get_comics(id=user['user_id'], show='all')
    collections = get_collections(id=user['user_id'])
    return render_template('workspace.html', comics=comics, collections=collections)


@bp.route('/contributors')
def contributors():
    database = db.Database()
    query = '''SELECT * FROM user ORDER BY full_name;'''
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


@bp.route('/archive')
def comic_archive():
    comics=get_comics()
    return render_template('archive.html', list=comics, type='comics')


@bp.route('/archive/collections')
def collection_archive():
    collections=get_collections()
    return render_template('archive.html',list=collections, type='collections')
