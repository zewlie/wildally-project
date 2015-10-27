"""Some sample data to use while building out Wildally"""


from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site

import csv
from datetime import datetime
from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    with open('seed_data/user.csv', 'rU') as users:
        users = csv.reader(users, dialect=csv.excel_tab)
        next(users)
        for row in users:

            row = row[0].rstrip()
            user_id, email, username, password = row.split(",")[:4]

        # email = user_data[0]
        # username = user_data[1]
        # password = user_data[2]

            account_made = datetime.now()

            user = User(id=user_id,
                        email=email,
                        username=username,
                        password=password,
                        account_made=account_made)

            # We need to add to the session or it won't ever be stored
            db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_orgs():
    """Load wildlife orgs from u.user into database."""

    print "Orgs"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Org.query.delete()

    # Read u.user file and insert data
    with open('seed_data/user.csv', 'rU') as users:
        users = csv.reader(users, dialect=csv.excel_tab)
        next(users)
        for row in users:

            row = row[0].rstrip()
            data = row.split(",")

            user_id = data[0]

            name = data[4]
            ein = data[5]
            show_address = data[6]
            address1 = data[7]
            address2 = data[8]
            city = data[9]
            state = data[10]
            zipcode = data[11]
            desc = data[12]
            phone = data[13]
            email = data[14]
            website = data[15]

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
                        email=email,
                        website=website)

            # We need to add to the session or it won't ever be stored
            db.session.add(org)

    # Once we're done, we should commit our work
    db.session.commit()


def load_pickups():
    """Load org pickups from u.pickup into database."""

    print "Pickups"


def load_hours():
    """Load org hours from u.hour into database."""

    print "Hours"


def load_org_animals():
    """Load org animal types from u.org_animal into association table in database."""

    print "OrgAnimals"


def load_animals():
    """Load animal types from u.animal into database."""

    print "Animals"


def load_contact_types():
    """Load contact types from u.contact_type into database."""

    print "ContactTypes"


def load_phones():
    """Load org phones from u.phone into database."""

    print "Phones"


def load_emails():
    """Load org emails from u.email into database."""

    print "Emails"


def load_site_types():
    """Load org site types from u.site_type into database."""

    print "SiteTypes"


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




