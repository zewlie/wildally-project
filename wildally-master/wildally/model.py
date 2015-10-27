"""Models and database functions for WildAlly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##############################################################################
# Model definitions

# User class
class User(db.Model):
    """ """

    __tablename__ = "users"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    account_made = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User id={} username={} email={} account_made={}>".format(self.id, self.username, self.email, self.account_made)


# Wildlife organization (special user) class
class Org(db.Model):
    """ """

    __tablename__ = "orgs"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    ein = db.Column(db.String(9))
    address1 = db.Column(db.String(100))
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(5))
    desc = db.Column(db.Text)
    phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Org id={} user_id={} name={} location={}, {}>".format(self.id, self.user_id, self.name, self.city, self.state)


# Pickup point/radius class
class Pickup(db.Model):
    """ """

    __tablename__ = "pickups"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    radius = db.Column(db.Float)
    

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


# Org <-> animals association class
class OrgAnimal(db.Model):
    """ """

    __tablename__ = "org_animals"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)
    priority = db.Column(db.Integer)


# Animal type class
class Animal(db.Model):
    """ """

    __tablename__ = "animals"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(300))


# Contact type class
class ContactType(db.model):
    """ """

    __tablename__ = "contact_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)


# (org) Phone class
class Phone(db.model):
    """ """

    __tablename__ = "phones"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('org_contacts.id'), nullable=False)
    number = db.Column(db.String(20), nullable=False)


# (org) Email class
class Email(db.model):
    """ """

    __tablename__ = "emails"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('org_contacts.id'), nullable=False)
    email = db.Column(db.String(50), nullable=False)


# (org) Social media class
class SiteType(db.model):
    """ """

    __tablename__ = "site_types"

    id = db.Column(db.String(50), nullable=False, primary_key=True)


# (org) Social media class
class Site(db.model):
    """ """

    __tablename__ = "sites"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('orgs.id'), nullable=False)
    type_id = db.Column(db.String(50), db.ForeignKey('site_types.id'), nullable=False)
    username = db.Column(db.String(50))
    url = db.Column(db.string(200))





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
