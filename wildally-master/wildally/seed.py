"""Some sample data to use while building out Wildally"""

from server import make_geocode
from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site

import csv
from passlib.hash import pbkdf2_sha256
from pygeocoder import Geocoder
from datetime import datetime

from model import connect_to_db, db
from server import app

user_csv_path = 'seed_data/rehabilitators_wa.csv'
animal_path = 'seed_data/u.animal'
contact_type_path = 'seed_data/u.contact_type'
site_type_path = 'seed_data/u.site_type'


def csv_to_tuples(file):
    """ Read the csv file and return a list of rows as tuples.
    This function assumes the csv file will start with a header. """

    list_of_tuples = []

    with open(file, 'rU') as users:
        users = csv.reader(users, dialect=csv.excel_tab)
        # Skip the header
        next(users)

        for row in users:
            row = row[0].rstrip()
            row = tuple(row.split(","))
            list_of_tuples.append(row)

    return list_of_tuples


def load_users():
    """Load users from user.csv into database."""

    print "Users"
    User.query.delete()

    data = csv_to_tuples(user_csv_path)

    for row in data:

        user_id = int(row[0])
        username = row[1]
        username = username.strip()
        username = username.replace(" ", "")
        username = username[:25]
        account_made = datetime.now()
        password = 'password'
        hash = pbkdf2_sha256.encrypt(password, rounds=1111, salt_size=16)

        user = User(id=user_id,
                    email='email@email.com',
                    username=username,
                    password=hash,
                    account_made=account_made)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

# Once we're done, we should commit our work
    db.session.commit()


def load_orgs():
    """ Load wildlife orgs from user.csv into database. """

    print "Orgs"
    Org.query.delete()

    # Read u.user file and insert data
    data = csv_to_tuples(user_csv_path)

    for row in data:

        user_id, name, show_address, address1, address2, city, state, zipcode, phone, desc = row[:10]

        org = Org(user_id=user_id,
                    name=name,
                    ein=None,
                    show_address=show_address, 
                    address1=address1,
                    address2=address2,
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    desc=desc,
                    phone=phone,
                    email=None,
                    website=None)

        # We need to add to the session or it won't ever be stored
        db.session.add(org)

    # Once we're done, we should commit our work
    db.session.commit()


def load_pickups():
    """ Convert addresses from user csv into coordinates; load into database. """

    print "Pickups"
    Pickup.query.delete()

    data = csv_to_tuples(user_csv_path)

    for row in data:

        user_id, name, show_address, address1, address2, city, state, zipcode, phone, desc = row[:10]

        # Only grab the address lines from users who want their addresses shown.
        # For everyone else, grab only city, state, and zipcode.
        # This ensures the privacy of users who want their addresses hidden.
        if show_address == '1':
            address = row[3:8]
        else:
            address = row[5:8]

        coords = make_geocode(address)

        pickup = Pickup(org_id=user_id,
                        latitude=coords[0],
                        longitude=coords[1])

        # We need to add to the session or it won't ever be stored
        db.session.add(pickup)

# Once we're done, we should commit our work
    db.session.commit()



def load_hours():
    """Load org hours from u.hour into database."""

    print "Hours"


def load_org_animals():
    """Load org animal typeseed_data/u.user" from u.org_animal into association table in database."""

    print "OrgAnimals"


def load_animals():
    """Load animal types from u.animal into database."""

    print "Animals"
    Animal.query.delete()

    for row in open(animal_path):
        name = row.rstrip()

        animal = Animal(name=name)

        db.session.add(animal)

    db.session.commit()


def load_contact_types():
    """Load contact types from u.contact_type into database."""

    print "ContactTypes"
    ContactType.query.delete()

    for row in open(contact_type_path):
        id = row.rstrip()

        contact_type = ContactType(id=id)

        db.session.add(contact_type)

    db.session.commit()


def load_phones():
    """Load org phones from u.phone into database."""

    print "Phones"


def load_emails():
    """Load org emails from u.email into database."""

    print "Emails"


def load_site_types():
    """Load org site types from u.site_type into database."""

    print "SiteTypes"
    SiteType.query.delete()

    for row in open(site_type_path):
        id = row.rstrip()

        site_type = SiteType(id=id)

        db.session.add(site_type)

    db.session.commit()


def load_sites():
    """Load org sites from u.site into database."""

    print "Sites"


##############################################################################


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_orgs()
    load_pickups()
    load_hours()
    load_org_animals()
    load_animals()
    load_contact_types()
    load_phones()
    load_emails()
    load_site_types()
    load_sites()




