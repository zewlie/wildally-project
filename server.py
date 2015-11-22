"""Wildally server."""

from jinja2 import StrictUndefined
from datetime import datetime, date, timedelta
from math import floor
from random import randint
from time import sleep
from PIL import Image

import json
import os
from flask import Flask, Markup, render_template, redirect, request, flash, session, jsonify, url_for, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
from redis import Redis
from celery import Celery
from werkzeug import secure_filename

from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site, Click, ClickFilter, connect_to_db, db

# Clicks for celery to process
GATHERED_CLICKS = []

# File upload settings
UPLOAD_FOLDER = './static/user/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'txt'])
THUMB_WIDTH = 200
THUMB_HEIGHT = 175

app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

# Functions not associated with particular routes
#################################################################################

def generate_thumb(filename, dimensions_tuple):
    thumb_dir = app.config['UPLOAD_FOLDER'] + 'thumb/' + str(session['user_id']) + '/'

    loaded_image = Image.open(app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/' + filename)
    loaded_image.load()

    cropped_image = loaded_image.crop(dimensions_tuple)
    thumb = cropped_image.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.ANTIALIAS)

    if os.path.lexists(thumb_dir) == False:
            os.makedirs(thumb_dir)

    thumb.save(os.path.join(thumb_dir, filename))

def grab_image_dimensions(filename):
    loaded_image = Image.open(app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/' + filename)
    loaded_image.load()

    return loaded_image.size

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def list_of_org_objects():
    orgs = db.session.query(Org).all()
    return orgs

def list_of_animal_objects():
    animals = db.session.query(Animal).all()
    return animals

def list_of_click_objects():
    clicks = db.session.query(Click).all()
    return clicks

def list_of_click_filter_objects():
    click_filters = db.session.query(ClickFilter).all()

def load_click_info_from_db():
    orgs = list_of_org_objects()
    animals = list_of_animal_objects()
    clicks = list_of_click_objects()
    click_filters = list_of_click_filter_objects()

    return (orgs, animals, clicks, click_filters)

def gather_clicks(org_id, current_filters):
    """ """

    click = Click(type_id="1",
                org_id=org_id,
                time=datetime.now())

    db.session.add(click)
    db.session.flush()
    db.session.commit()

    if current_filters:
        for each in current_filters:
            click_filter = ClickFilter(click_id=click.id,
                                       filter_id=each)
            db.session.add(click_filter)
        db.session.commit()

    return

# def insert_clicks_into_db(gathered_clicks_list):
#     """ """

#     for single_click in gathered_clicks_list:

#         click_type_id, click_org_id, click_time, click_filters = single_click

#         click = Click(type_id=click_type_id,
#                     org_id=click_org_id,
#                     time=click_time)

#         db.session.add(click)
#         db.session.flush()
#         db.session.commit()

#         if current_filters:
#             for each in current_filters:
#                 click_filter = ClickFilter(click_id=click.id,
#                                            filter_id=each)
#                 db.session.add(click_filter)
#             db.session.commit()

#     return

# def gather_clicks(org_id, current_filters):
#     """ """
#     global GATHERED_CLICKS

#     click_type_id = 1,
#     click_org_id = org_id,
#     click_time = datetime.now()
#     click_filters = []

#     if current_filters:
#         for each in current_filters:
#             click_filters.append(each)

#     GATHERED_CLICKS.append([click_type_id, click_org_id, click_time, click_filters])
#     print GATHERED_CLICKS

#     return

##################################################


@app.route('/_track-click', methods=['GET', 'POST'])
def track_click():
    """Grab click info from map, send through to celery worker."""
    
    org_id = request.form.get("orgId")
    current_filters = request.form.get("currentFilters")

    if current_filters == "filters&":
        current_filters = None

    else:
        current_filters = current_filters.strip("filters&")
        current_filters = current_filters.split("&")

    gather_clicks(org_id, current_filters)

    return jsonify({"success": "yes"})


@app.route('/')
def index():
    """Homepage."""

    if 'user_id' not in session:
        session['user_id'] = None

    return render_template('index.html')

@app.route('/login')
def login():
    """Login page."""

    return render_template('login.html')


@app.route('/login-success', methods=['POST'])
def login_success():
    """Login form submission."""

    username = request.form.get("username")
    password = request.form.get("password")
    user = db.session.query(User).filter(User.username == username).one()
    passcheck = user.verify_pw(password)

    if user is None or passcheck is False:
        if user:
            flash("Whoops, did you forget your password?")
        else:
            flash(Markup("That username doesn't appeared to be registered. <a href='/new'>Register now</a>?"))

        session['user_id'] = None

        return redirect('/login')

    elif user.username == username and passcheck is True:
        flash("Welcome back, {}!".format(user.username))

        session['user_id'] = user.id
        user.last_login = datetime.now()
        db.session.commit()

    #### TODO: redirect to previous page
    return redirect('/') # redirect to homepage


@app.route('/logout')
def logout():
    """Logout and redirect to homepage."""

    session['user_id'] = None

    flash("Successfully logged out!")

    return redirect('/')

@app.route('/new')
def create_user():
    """Create a new user."""

    return render_template('new_account.html')

@app.route('/user-added', methods=['POST'])
def user_added():
    """Login form submission."""

    # Basic user fields:
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    account_made = datetime.now()

    user = User(email=email,
                username=username,
                password=password,
                account_made=account_made)

    db.session.add(user)
    db.session.commit()

    # Check if the user is affiliated with an org:
    is_org = request.form.get("is-org")

    # If so, insert data into orgs and pickups:
    if is_org == 'yes':

        # Wildlife rehabilitator org fields:
        name = request.form.get("org-name")
        ein = request.form.get("ein")
        show_address = request.form.get("show-address")
        address1 = request.form.get("address1")
        address2 = request.form.get("address2")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("zipcode")
        desc = request.form.get("desc")
        phone = request.form.get("phone")
        org_email = request.form.get("org-email")
        website = request.form.get("website")

        user = db.session.query(User).filter(User.email == email).one()
        user_id = user.id

        org = Org(user_id=user_id,
                    name=name,
                    ein=ein,
                    show_address=show_address,
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    desc=desc,
                    phone=phone,
                    email=org_email,
                    website=website)

        db.session.add(org)
        db.session.commit()

        # Insert into pickups:
        org = db.session.query(Org).filter(Org.user_id == user_id).one()
        org_id = org.id

        if show_address == '1':
            address = [address1, address2, city, state, zipcode]
        else:
            address = [city, state, zipcode]

        coords = Org.make_geocode()

        pickup = Pickup(org_id=org_id,
                        latitude=coords[0],
                        longitude=coords[1])

        db.session.add(pickup)
        db.session.commit()

     # Automatically log the new user in

    user = db.session.query(User).filter(User.email == email).one()

    session['user_id'] = user.id

    flash("Welcome to WildAlly, {}!".format(username))

    return redirect('/settings')


@app.route('/settings')
def manage_account():
    """Manage user account."""

    user_id = session['user_id']
    user = db.session.query(User).filter(User.id == user_id).first()
    org = db.session.query(Org).filter(Org.user_id == user_id).first()

    if org:
        is_org = 1
    else:
        is_org = 0

    return render_template('settings.html', is_org=is_org,
                                            username=user.username, 
                                            email=user.email,
                                            org_name=org.name,
                                            ein=org.ein,
                                            show_address=org.show_address,
                                            address1=org.address1,
                                            address2=org.address2,
                                            city=org.city,
                                            state=org.state,
                                            zipcode=org.zipcode,
                                            desc=org.desc,
                                            phone=org.phone,
                                            org_email= org.email,
                                            website=org.website,
                                            accept_animals=org.accept_animals,
                                            accept_volunteers=org.accept_volunteers)

@app.route('/_update-settings')
def update_settings():

    attributes = {'user': ['username',
                            'email',
                            'password'],
                  'org': ['org-name',
                        'ein',
                        'desc',
                        'phone',
                        'org-email',
                        'website',
                        'accept_animals',
                        'accept_volunteers']
                        }

    user_id = session['user_id']
    setting_name = request.args.get("settingName")
    setting_value = request.args.get("settingValue")

    if setting_name in attributes['user']:

        user = db.session.query(User).filter(User.id == user_id).first()
        if setting_name == 'password':
            setting_value = user.hash_pw(setting_value)
        setattr(user, setting_name, setting_value)
        db.session.commit()

        if setting_name == 'username':
            session['username'] = setting_value

        if getattr(user, setting_name) == setting_value:
            return jsonify({'success': 'yes'})

    elif setting_name in attributes['org']:
        setting_name = setting_name.replace('org-','')
        org = db.session.query(Org).filter(Org.user_id == user_id).first()
        setattr(org, setting_name, setting_value)
        db.session.commit()

        if getattr(org, setting_name) == setting_value:
            return jsonify({'success': 'yes'})

    # TODO: this is missing a failure check.
    elif setting_name == 'address':
        org = db.session.query(Org).filter(Org.user_id == user_id).first()
        address1, address2, city, state, zipcode, show_address = setting_value.split('+')
        setattr(org, 'address1', address1)
        setattr(org, 'address2', address2)
        setattr(org, 'city', city)
        setattr(org, 'state', state)
        setattr(org, 'zipcode', zipcode)
        setattr(org, 'show_address', show_address)
        db.session.commit()

        coords = org.make_geocode()

        pickup = db.session.query(Pickup).filter(Pickup.org_id == org.id).first()
        setattr(pickup, 'latitude', coords[0])
        setattr(pickup, 'longitude', coords[1])
        db.session.commit()

        return jsonify({'success': 'yes'})


    return jsonify({'success': 'no'})


# @app.route('/uploads/<filename>')
# def uploaded_photo(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'] + str(session['user_id']) + '/img',filename)


@app.route('/photos', methods=['GET', 'POST'])
def manage_photos():
    thumb_dir = app.config['UPLOAD_FOLDER'] + 'thumb/' + str(session['user_id']) + '/'

    file_count = 0
    if os.path.lexists(thumb_dir):
        for root, dirs, filenames in os.walk(thumb_dir):
            root = root
            filenames = filenames

            for filename in filenames:
                file_count += 1
    else:
        root = None
        filenames = None

    return render_template('photos.html', file_count=file_count, root=root, filenames=filenames)

@app.route('/_upload-photo', methods=['POST'])
def upload_photo():
    photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'
    print "WOOP"
    photo_file = request.files['photo']
    print "WOOP 2"
    if photo_file and allowed_file(photo_file.filename):
        print "WOOP3"
        filename = secure_filename(photo_file.filename)
        print "WOOP4"
        if os.path.lexists(photo_dir) == False:
            os.makedirs(photo_dir)

        photo_file.save(os.path.join(photo_dir, filename))

        image_dimensions = grab_image_dimensions(filename)
        print image_dimensions

        image_width, image_height = image_dimensions

        width_factor = float(image_width) / THUMB_WIDTH
        height_factor = float(image_height) / THUMB_HEIGHT

        if width_factor > height_factor:
            excess_width = int(((image_width / height_factor) - THUMB_WIDTH) * height_factor)
            crop_right = image_width - (excess_width / 2)
            crop_left = excess_width / 2

            crop_thumb = (crop_left, 0, crop_right, image_height)\

            thumb = generate_thumb(filename, crop_thumb)

        elif height_factor > width_factor:
            excess_height = int(((image_height / width_factor) - THUMB_HEIGHT) * width_factor)
            crop_bottom = image_height - (excess_height / 2)
            crop_top = excess_width / 2

            crop_thumb = (0, crop_top, image_width, crop_bottom)

            thumb = generate_thumb(filename, crop_thumb)

        elif height_factor == width_factor:
            pass

        print width_factor, height_factor
        # return redirect(url_for('uploaded_photo',
        #                         filename=filename))
        return redirect('/photos')
    return jsonify({'success': 'no'})


@app.route('/analytics')
def show_analytics():

    return render_template('analytics.html')


@app.route('/orgs.json')
def org_info():
    """JSON information about orgs."""

    photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'

    orgs = {
        org.id: {
            "orgName": org.name,
            "address1" : org.address1,
            "address2" : org.address2,
            "city": org.city,
            "state": org.state,
            "zipcode": org.zipcode,
            "desc": org.desc,
            "phone": org.phone,
            "email": org.email,
            "website": org.website,
            "latitude": org.pickups[0].latitude,
            "longitude": org.pickups[0].longitude,
            "acceptAnimals": org.accept_animals,
            "acceptVolunteers": org.accept_volunteers,
            "animals": [],
            "photoRoot": None,
            "photoFilenames": None,
            "photoCount": 0,
        } for org in Org.query.all()}

    rows = Org.query.all()
    for org in rows:
        photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'
        if os.path.lexists(photo_dir):
            for root, dirs, filenames in os.walk(photo_dir):
                orgs[org.id]["photoRoot"]= root
                orgs[org.id]["photoFilenames"] = filenames
                for filename in filenames:
                    orgs[org.id]["photoCount"] += 1

    org_animals = {}

    rows = OrgAnimal.query.all()
    for org in rows:
        org.type_id = [str(org.type_id)]
        orgs[org.org_id]["animals"].extend(org.type_id)

    return jsonify(orgs)

@app.route('/animals.json')
def animal_info():
    """JSON information about animal types."""

    photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'

    animals = {
        animal.id: {
            "typeName": animal.name,
            "desc" : animal.desc,
        } for animal in Animal.query.all()}

    return jsonify(animals)


@app.route('/analytics.json')
def analytics_json():

    org_id = session['user_id']

    with open(os.path.join(app.config['UPLOAD_FOLDER'] + "analytics/analytics_" + str(org_id) + ".txt")) as analytics_json:
        json_content = analytics_json.read().replace("[u'", '["').replace("'", '"')

    analytics_json.close()

    return json_content


celery = Celery(app)
celery.config_from_object('celeryconfig')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    connect_to_db(app)

    # # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
