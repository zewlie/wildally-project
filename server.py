"""Wildally server."""

from jinja2 import StrictUndefined
from datetime import datetime

from flask import Flask, Markup, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from redis import Redis
from celery import Celery

from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

# Redis
# redis = Redis()

# Functions not associated with particular routes
#################################################################################


@app.route('/')
def index():
    """Homepage."""

    if 'username' not in session:
        session['username'] = None

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
    user = db.session.query(User).filter(User.username == username).first()
    passcheck = user.verify_pw(password)

    if user is None or passcheck is False:
        if user:
            flash("Whoops, did you forget your password?")
        else:
            flash(Markup("That username doesn't appeared to be registered. <a href='/new'>Register now</a>?"))

        session['username'] = None

        return redirect('/login')

    elif user.username == username and passcheck is True:
        flash("Welcome back, {}!".format(user.username))

        session['username'] = username
        user.last_login = datetime.now()
        db.session.commit()

    #### TODO: redirect to previous page
    return redirect('/') # redirect to homepage


@app.route('/logout')
def logout():
    """Logout and redirect to homepage."""

    session['username'] = None

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
    session['username'] = username

    flash("Welcome to WildAlly, {}!".format(username))

    return redirect('/settings')


@app.route('/settings')
def manage_account():
    """Manage user account."""

    username = session['username']
    user = db.session.query(User).filter(User.username == username).first()
    org = db.session.query(Org).filter(Org.user_id == user.id).first()

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


@app.route('/orgs.json')
def org_info():
    """JSON information about orgs."""

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
            "animals": []
        } for org in Org.query.all()}

    org_animals = {}

    rows = OrgAnimal.query.all()
    for org in rows:
        org.type_id = [str(org.type_id)]
        orgs[org.org_id]["animals"].extend(org.type_id)

    return jsonify(orgs)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()