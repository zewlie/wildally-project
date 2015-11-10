"""Models and database functions for WildAlly."""

from flask_sqlalchemy import SQLAlchemy
from pygeocoder import Geocoder
from passlib.hash import pbkdf2_sha256
import time

db = SQLAlchemy()


##############################################################################
# Model definitions

# User class
class User(db.Model):
    """ """

    __tablename__ = "users"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    account_made = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User id={} username={} email={} account_made={}>".format(self.id, self.username, self.email, self.account_made)

    def __init__(self, email, username, password, account_made):
        self.email = email
        self.username = username
        self.password = self.hash_pw(password)
        self.account_made = account_made

    def hash_pw(self, password):
        """Hash & salt password."""

        return pbkdf2_sha256.encrypt(password, rounds=1111, salt_size=16)

    def verify_pw(self, password):
        """Verify password."""

        return pbkdf2_sha256.verify(password, self.password)


# Wildlife organization (special user) class
class Org(db.Model):
    """ """

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
        """Provide helpful representation when printed."""

        return "<Org id={} user_id={} name={} location={}, {}>".format(self.id, self.user_id, self.name, self.city, self.state)

    def make_geocode(self):
        """ Generate geocode from a list of address attributes, e.g. [street, city, state]. """

        if self.show_address == 1:
            address = [self.address1, self.address2, self.city, self.state, self.zipcode]
        else:
            address = [self.city, self.state, self.zipcode]

        address = " ".join(address)
        lookup = Geocoder.geocode(address)
        coords = lookup[0].coordinates

        time.sleep(1)
        return coords

# Pickup point/radius class
class Pickup(db.Model):
    """ """

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
    

# Hours (open hours for organizations) class
class Hour(db.Model):
    """ """

    __tablename__ = "hours"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    # Weekday set to int, maybe string would be better?
    weekday = db.Column(db.Integer, nullable=False)
    start_hour = db.Column(db.Float, nullable=True)
    end_hour = db.Column(db.Float, nullable=True)
    closed = db.Column(db.Boolean, default=False)

    org = db.relationship("Org",
                            backref=db.backref("hours"))


# Org <-> animals association class
class OrgAnimal(db.Model):
    """ """

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


# Animal type class
class Animal(db.Model):
    """ """

    __tablename__ = "animals"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Animal id={} name={} desc={}>".format(self.id, self.name, self.desc)


# Contact type class
class ContactType(db.Model):
    """ """

    __tablename__ = "contact_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ContactType id={}>".format(self.id)

# (org) Phone class
class Phone(db.Model):
    """ """

    __tablename__ = "phones"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('contact_types.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)

    org = db.relationship("Org",
                            backref=db.backref("phones"))

    contact_type = db.relationship("ContactType",
                            backref=db.backref("phones"))


# (org) Email class
class Email(db.Model):
    """ """

    __tablename__ = "emails"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('contact_types.id'), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    org = db.relationship("Org",
                            backref=db.backref("emails"))

    contact_type = db.relationship("ContactType",
                            backref=db.backref("emails"))


# (org) Social media class
class SiteType(db.Model):
    """ """

    __tablename__ = "site_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<SiteType id={}>".format(self.id)

# (org) Social media class
class Site(db.Model):
    """ """

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


# Volunteer applications
class Volunteer(db.Model):
    """ """

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


# Volunteer opportunities with orgs
class VolunteerJob(db.Model):
    """ """

    __tablename__ = "volunteer_jobs"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("jobs"))


# Educational courses offered by orgs
class Course(db.Model):
    """ """

    __tablename__ = "courses"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    time = db.Column(db.DateTime)
    desc = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))

    org = db.relationship("Org",
                            backref=db.backref("courses"))







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
