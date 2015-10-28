"""Wildally server."""

from jinja2 import StrictUndefined

from flask import Flask, Markup, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from pygeocoder import Geocoder
from datetime import datetime

from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    if 'email' not in session:
        session['email'] = None
    if 'password' not in session:
        session['password'] = None

    return render_template('index.html')

@app.route('/login')
def login():
    """Login page."""

    return render_template('login.html')


@app.route('/login-success', methods=['POST'])
def login_success():
    """Login form submission."""

    session['email'] = request.form.get("email")
    session['password'] = request.form.get("password")

    user = db.session.query(User).filter(User.email == session['email']).first()

    if user is None or user.password != session['password']:
        if user:
            flash("Whoops, did you forget your password?")
        else:
            flash(Markup("That email doesn't appeared to be registered. <a href='/new'>Register now</a>?"))

        session['email'] = None
        session['password'] = None

        return redirect('/login')

    elif user.email == session['email'] and user.password == session['password']:
        flash("Welcome back, {}!".format(user.username))

    #### TODO: redirect to previous page
    return redirect('/') # redirect to homepage


@app.route('/logout')
def logout():
    """Logout and redirect to homepage."""

    session['email'] = None
    session['password'] = None

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

        address = " ".join(address)

        lookup = Geocoder.geocode(address)
        coords = lookup[0].coordinates

        pickup = Pickup(org_id=org_id,
                        latitude=coords[0],
                        longitude=coords[1])

        db.session.add(pickup)
        db.session.commit()

     # Automatically log the new user in
    session['email'] = email
    session['password'] = password

    flash("Welcome to WildAlly, {}!".format(username))

    return redirect('/settings')


@app.route('/settings')
def manage_account():
    """Manage user account."""

    return render_template('settings.html')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()