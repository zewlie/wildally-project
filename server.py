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

# Photo upload settings
UPLOAD_FOLDER = './static/user/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'txt'])
THUMB_WIDTH = 200
THUMB_HEIGHT = 175

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Photo upload max size: 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Force Jinja to send error messages when variables are undefined
app.jinja_env.undefined = StrictUndefined


# Routes
#################################################################################

@app.route('/_track-click', methods=['GET', 'POST'])
def track_click():
    """Grabs click info from a request on the map and inserts it into the DB."""
    
    org_id = request.form.get("orgId")
    current_filters = request.form.get("currentFilters")

    # Transform the filters string into a list.
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

    # New visitors won't have a 'user_id' session variable.
    # We create one here:
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
    pass_check = user.verify_pw(password)

    if user is None or pass_check is False:
        if user:
            flash("Whoops, did you forget your password?")
        else:
            flash(Markup("That username doesn't appeared to be registered. <a href='/new'>Register now</a>?"))

        return redirect('/login')

    elif user.username == username and pass_check is True:
        flash("Welcome back, {}!".format(user.username))
        session['user_id'] = user.id

        # Update the user's last login.
        user.last_login = datetime.now()
        db.session.commit()

    ## TODO: redirect to previous page
    return redirect('/') # redirect to homepage


@app.route('/logout')
def logout():
    """Logout and redirect to homepage."""

    session['user_id'] = None
    flash("Successfully logged out!")

    return redirect('/')


@app.route('/new')
def create_user():
    """Form for account creation."""

    return render_template('new_account.html')


@app.route('/user-added', methods=['POST'])
def user_added():
    """New account form submission."""

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
    db.session.flush()
    db.session.commit()

    # Automatically log the new user in
    session['user_id'] = user.id
    flash("Welcome to WildAlly, {}!".format(username))

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

        org = Org(user_id=user.id,
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
        db.session.flush()

        # Create geocode and insert coordinates into pickups:
        if show_address == '1':
            address = [address1, address2, city, state, zipcode]
        else:
            address = [city, state, zipcode]

        coords = Org.make_geocode()

        pickup = Pickup(org_id=org.id,
                        latitude=coords[0],
                        longitude=coords[1])

        db.session.add(pickup)
        db.session.commit()

    return redirect('/settings')


@app.route('/settings')
def manage_account():
    """Manage user account."""

    user_id = session['user_id']
    # Check if the user is associated with an org
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
    """Updates account settings."""

    user_id = session['user_id']
    user = db.session.query(User).filter(User.id == user_id).first()

    setting_name = request.args.get("settingName")
    setting_type = account_setting_type(setting_name)
    setting_value = request.args.get("settingValue")

    if setting_type == 'user':
        return user.update_setting(setting_name, setting_value)

    if setting_type == 'org':
        org = user.org[0]
        return org.update_setting(setting_name, setting_value)

    elif setting_name == 'address':
        org = user.org[0]
        return org.update_address(setting_value)

    return jsonify({'success': 'no'})


@app.route('/photos')
def manage_photos():
    """Photos page; displays all uploaded thumbnails."""

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
    """Upload a new photo and automatically generate a thumbnail for it."""

    photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'
    photo_file = request.files['photo']

    if photo_file and allowed_file(photo_file.filename):
        filename = secure_filename(photo_file.filename)

        # If this is the user's first upload, create their img directory.
        if os.path.lexists(photo_dir) == False:
            os.makedirs(photo_dir)

        photo_file.save(os.path.join(photo_dir, filename))

        # Generate a thumbnail image.
        crop_and_generate_thumb(filename)

        return redirect('/photos')

    return redirect('/photos')


@app.route('/_remove-photo')
def remove_photo():
    """Remove a photo."""

    photo_dir = app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/'
    thumb_dir = app.config['UPLOAD_FOLDER'] + 'thumb/' + str(session['user_id']) + '/'

    filename = request.args.get("photoId")
    os.remove(photo_dir + filename)
    os.remove(thumb_dir + filename)

    return jsonify({'success': 'yes'})


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
        photo_dir = app.config['UPLOAD_FOLDER'] + 'thumb/' + str(org.id) + '/'
        # Check if the org has any photos uploaded.
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
        # Reformat for JSON parser
        json_content = analytics_json.read().replace("[u'", '["').replace("'", '"')

    analytics_json.close()

    return json_content


# Helper functions
#################################################################################

def account_setting_type(attribute):
    """Determines the type of user/org attribute being updated from the Settings page."""

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

    if attribute in attributes['user']:
        return 'user'
    elif attribute in attributes['org']:
        return 'org'
    elif attribute == 'address':
        return 'address'


def crop_and_generate_thumb(filename):
    """Crops an uploaded photo and generates a thumbnail from the cropped version."""

    image_dimensions = grab_image_dimensions(filename)
    image_width, image_height = image_dimensions

    # Crop from whichever dimension produces the higher number here:
    width_factor = float(image_width) / THUMB_WIDTH
    height_factor = float(image_height) / THUMB_HEIGHT

    # If the image is too wide, crop off half the excess width from each side.
    if width_factor > height_factor:
        excess_width = int(((image_width / height_factor) - THUMB_WIDTH) * height_factor)
        crop_right = image_width - (excess_width / 2)
        crop_left = excess_width / 2
        crop_thumb = (crop_left, 0, crop_right, image_height)

    #If the image is too tall, crop off half the excess height from the top and bottom.
    elif height_factor > width_factor:
        excess_height = int(((image_height / width_factor) - THUMB_HEIGHT) * width_factor)
        crop_bottom = image_height - (excess_height / 2)
        crop_top = excess_width / 2
        crop_thumb = (0, crop_top, image_width, crop_bottom)

    #If the image has the correct dimensions, preserve them.
    elif height_factor == width_factor:
        crop_thumb (0, 0, image_width, image_height)
    
    thumb = generate_thumb(filename, crop_thumb)


def generate_thumb(filename, dimensions_tuple):
    """Generates a thumbnail from an uploaded image."""

    thumb_dir = app.config['UPLOAD_FOLDER'] + 'thumb/' + str(session['user_id']) + '/'

    loaded_image = Image.open(app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/' + filename)
    loaded_image.load()

    cropped_image = loaded_image.crop(dimensions_tuple)
    thumb = cropped_image.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.ANTIALIAS)

    if os.path.lexists(thumb_dir) == False:
            os.makedirs(thumb_dir)

    thumb.save(os.path.join(thumb_dir, filename))


def grab_image_dimensions(filename):
    """Returns (width, height) tuple of an uploaded photo."""

    loaded_image = Image.open(app.config['UPLOAD_FOLDER'] + 'img/' + str(session['user_id']) + '/' + filename)
    loaded_image.load()

    return loaded_image.size


def allowed_file(filename):
    """Checks whether an uploaded file is an acceptable file type."""

    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def gather_clicks(org_id, current_filters):
    """Adds a new click and its associated filters to the database."""

    click = Click(type_id="1",
                org_id=org_id,
                time=datetime.now())

    db.session.add(click)
    db.session.flush() # This is how we access the click.id for the ClickFilter insertion.

    if current_filters:
        for each in current_filters:
            click_filter = ClickFilter(click_id=click.id,
                                       filter_id=each)
            db.session.add(click_filter)

    db.session.commit()

    return None


def load_click_info_from_db():
    """Loads all the information needed to generate analytics JSON files."""

    orgs = Org.list_of_org_objects()
    animals = Animal.list_of_animal_objects()
    clicks = Click.list_of_click_objects()
    click_filters = ClickFilter.list_of_click_filter_objects()

    return (orgs, animals, clicks, click_filters)


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
