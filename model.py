"""Models and database functions for WildAlly."""

from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from datetime import datetime
from random import randint
from pygeocoder import Geocoder
from passlib.hash import pbkdf2_sha256
import time

db = SQLAlchemy()


##############################################################################
# Model definitions


class User(db.Model):
    """Basic user class."""

    __tablename__ = "users"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    account_made = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        """Provides helpful representation when printed."""

        return "<User id={} username={} email={} account_made={}>".format(self.id, self.username, self.email, self.account_made)

    def __init__(self, email, username, password, account_made):
        self.email = email
        self.username = username
        self.password = self.hash_pw(password)
        self.account_made = account_made

    def hash_pw(self, password):
        """Hashes & salts password."""

        return pbkdf2_sha256.encrypt(password, rounds=1111, salt_size=16)

    def verify_pw(self, password):
        """Verifies password; returns True when password matches user's account."""

        return pbkdf2_sha256.verify(password, self.password)

    def update_setting(self, setting_name, setting_value):
        """Updates an attribute on the user account."""

        if setting_name == 'password':
            setting_value = self.hash_pw(setting_value)
        setattr(self, setting_name, setting_value)
        db.session.commit()

        if getattr(self, setting_name) == setting_value:
            return jsonify({'success': 'yes'})

    @staticmethod
    def generate_unique_username(username):
        """Checks if the username already exists; if so, appends a random int to make it unique."""

        username_match = db.session.query(User).filter(User.username == username).first()

        if username_match:
            while username_match.username == username:
                username = username[:24] + str(randint(0,9))

        return username
        

class Org(db.Model):
    """Org user class; holds additional user info."""

    __tablename__ = "orgs"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    ein = db.Column(db.String(9))
    show_address = db.Column(db.Boolean, nullable=False)
    address1 = db.Column(db.String(100))
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(5))
    desc = db.Column(db.Text)
    phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    accept_animals = db.Column(db.Boolean)
    accept_volunteers = db.Column(db.Boolean)

    user = db.relationship("User",
                            backref=db.backref("org"))

    def __repr__(self):
        """Provides helpful representation when printed."""

        return "<Org id={} user_id={} name={} location={}, {}>".format(self.id, self.user_id, self.name, self.city, self.state)

    @staticmethod
    def list_of_org_objects():
        """Returns a list of objects representing all rows in orgs."""
        orgs = db.session.query(Org).all()
        return orgs

    def make_geocode(self):
        """Generates geocode from a list of address attributes, e.g. [street, city, state]."""

        if self.show_address == 1:
            address = [self.address1, self.address2, self.city, self.state, self.zipcode]
        else:
            address = [self.city, self.state, self.zipcode]

        address = " ".join(address)
        lookup = Geocoder.geocode(address)
        coords = lookup[0].coordinates

        time.sleep(0.2)
        return coords

    def update_setting(self, setting_name, setting_value):
        """Updates an attribute on the org account."""

        setting_name = setting_name.replace('org-','')
        setattr(self, setting_name, setting_value)
        db.session.commit()

        if getattr(self, setting_name) == setting_value:
            return jsonify({'success': 'yes'})

    def update_address(self, address_string):
        """Updates the address fields on the org account and the associated geocode in pickups."""

        address1, address2, city, state, zipcode, show_address = address_string.split('+')
        setattr(self, 'address1', address1)
        setattr(self, 'address2', address2)
        setattr(self, 'city', city)
        setattr(self, 'state', state)
        setattr(self, 'zipcode', zipcode)
        setattr(self, 'show_address', show_address)
        db.session.commit()

        pickup = self.pickups[0]
        coords = self.make_geocode()
        setattr(pickup, 'latitude', coords[0])
        setattr(pickup, 'longitude', coords[1])
        db.session.commit()

        return jsonify({'success': 'yes'})


class Pickup(db.Model):
    """Class for org locations/pickup points."""

    __tablename__ = "pickups"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    radius = db.Column(db.Float)

    org = db.relationship("Org",
                            backref=db.backref("pickups"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Pickup org_id={} latitude={} longitude={} radius={}>".format(self.org_id, self.latitude, self.longitude, self.radius)
    

class Hour(db.Model):
    """Class for org open hours."""

    __tablename__ = "hours"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    ## TODO: Weekday set to int, maybe string would be better?
    weekday = db.Column(db.Integer, nullable=False)
    start_hour = db.Column(db.Float, nullable=True)
    end_hour = db.Column(db.Float, nullable=True)
    closed = db.Column(db.Boolean, default=False)

    org = db.relationship("Org",
                            backref=db.backref("hours"))


class OrgAnimal(db.Model):
    """Class for connections between orgs and animals."""

    __tablename__ = "org_animals"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)
    priority = db.Column(db.Integer)

    org = db.relationship("Org",
                            backref=db.backref("org_animals"))

    animal = db.relationship("Animal",
                            backref=db.backref("org_animals"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<OrgAnimal org_id={} type_id={} name={}>".format(self.org_id, self.type_id, self.animal.name)


class Animal(db.Model):
    """Class for animal types that orgs may accept."""

    __tablename__ = "animals"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Animal id={} name={} desc={}>".format(self.id, self.name, self.desc)

    @staticmethod
    def list_of_animal_objects():
        """Returns a list of objects representing all rows in animals."""

        animals = db.session.query(Animal).all()
        return animals


class ContactType(db.Model):
    """Class for org contact types."""

    __tablename__ = "contact_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ContactType id={}>".format(self.id)


class Phone(db.Model):
    """Class for org phone numbers."""

    __tablename__ = "phones"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('contact_types.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)

    org = db.relationship("Org",
                            backref=db.backref("phones"))

    contact_type = db.relationship("ContactType",
                            backref=db.backref("phones"))


class Email(db.Model):
    """Class for org email addresses."""

    __tablename__ = "emails"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('contact_types.id'), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    org = db.relationship("Org",
                            backref=db.backref("emails"))

    contact_type = db.relationship("ContactType",
                            backref=db.backref("emails"))


class SiteType(db.Model):
    """Class for org website/social media account types."""

    __tablename__ = "site_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<SiteType id={}>".format(self.id)


class Site(db.Model):
    """Class for org websites/social media links."""

    __tablename__ = "sites"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('site_types.id'), nullable=False)
    username = db.Column(db.String(50))
    url = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("sites"))

    site_type = db.relationship("SiteType",
                            backref=db.backref("sites"))


class Volunteer(db.Model):
    """Class for volunteer applicants."""

    __tablename__ = "volunteers"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('volunteer_jobs.id'), nullable=False)
    desc = db.Column(db.Text)
    phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    photo = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("volunteers"))

    user = db.relationship("User",
                            backref=db.backref("volunteers"))

    job = db.relationship("VolunteerJob",
                            backref=db.backref("volunteers"))


class VolunteerJob(db.Model):
    """Class for open volunteer jobs."""

    __tablename__ = "volunteer_jobs"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("jobs"))


class Course(db.Model):
    """Class for educational courses offered by orgs."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    time = db.Column(db.DateTime)
    desc = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("courses"))


class Click(db.Model):
    """Class for map marker clicks."""

    __tablename__ = "clicks"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org",
                            backref=db.backref("clicks"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Click id={} type_id={} org_id={} time={}>".format(self.id, self.type_id, self.org_id, self.time)

    @staticmethod
    def list_of_click_objects():
        """Returns a list of objects representing all rows in clicks."""

        clicks = db.session.query(Click).all()
        return clicks


class ClickFilter(db.Model):
    """Class for filters associated with clicks on map markers."""

    __tablename__ = "click_filters"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    click_id = db.Column(db.Integer, db.ForeignKey('clicks.id'), nullable=False)
    filter_id = db.Column(db.String(50), nullable=False)

    click = db.relationship("Click",
                            backref=db.backref("click_filters"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ClickFilter id={} click_id={} filter_id={}>".format(self.id, self.click_id, self.filter_id)

    @staticmethod
    def list_of_click_filter_objects():
        """Returns a list of objects representing all rows in click_filters."""

        click_filters = db.session.query(ClickFilter).all()
        return click_filters


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wildally.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
