"""Wildally server."""

from jinja2 import StrictUndefined

from flask import Flask, Markup, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

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
        flash("Welcome, {}!".format(user.username))

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

@app.route('/user-added')
def user_added():
    """New user form submission."""

    return "Placeholder"

@app.route('/settings')
def manage_account():
    """Manage user account."""

    return "Placeholder"

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()