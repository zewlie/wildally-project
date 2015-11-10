"""Some sample data to use while building out Wildally"""

from model import User, Org, Pickup, Animal, ContactType, SiteType, OrgAnimal

import csv
from datetime import datetime

from model import connect_to_db, db
from server import app

user_csv_path = 'seed_data/rehabilitators.csv'
org_animal_csv_path = 'seed_data/animal_org.csv'
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

        username = row[1]
        username = username.strip()
        username = username.replace(" ", "")
        username = username[:25]
        account_made = datetime.now()

        user = User(email='email@email.com',
                    username=username,
                    password='password',
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

        user_id, name, show_address, address1, address2, city, state, zipcode, phone, desc, accept_volunteers = row[:11]

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
                    website=None,
                    accept_animals=1,
                    accept_volunteers=accept_volunteers)

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

        org_id = row[0]
        org = Org.query.get(org_id)

        coords = org.make_geocode()

        pickup = Pickup(org_id=org_id,
                        latitude=coords[0],
                        longitude=coords[1])

        # We need to add to the session or it won't ever be stored
        db.session.add(pickup)

# Once we're done, we should commit our work
    db.session.commit()


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


def load_site_types():
    """Load org site types from u.site_type into database."""

    print "SiteTypes"
    SiteType.query.delete()

    for row in open(site_type_path):
        id = row.rstrip()

        site_type = SiteType(id=id)

        db.session.add(site_type)

    db.session.commit()


def load_org_animals():
    """ """

    print "OrgAnimals"
    OrgAnimal.query.delete()

    # Read u.user file and insert data
    data = csv_to_tuples(org_animal_csv_path)

    for row in data:

        org_id, type_id = row[:2]

        org_animal = OrgAnimal(org_id=org_id, type_id=type_id)

        # We need to add to the session or it won't ever be stored
        db.session.add(org_animal)

    # Once we're done, we should commit our work
    db.session.commit()


##############################################################################


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_orgs()
    load_pickups()
    load_animals()
    load_contact_types()
    load_site_types()
    load_org_animals()
