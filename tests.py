import json
from unittest import TestCase
from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site, Click, ClickFilter, db
from server import app
import flask
import server


class WildAllyUnitTestCase(TestCase):
    """Discrete code testing."""

    def test_account_setting_type(self):
        self.assertEqual(server.account_setting_type("address"), 'address')
        self.assertEqual(server.account_setting_type("org-email"), 'org')
        self.assertEqual(server.account_setting_type("email"), 'user')

    def test_allowed_file(self):
        self.assertEqual(server.allowed_file("image.png"), True)
        self.assertEqual(server.allowed_file("image.pdf"), False)


class MockFlaskTests(TestCase):
    """Flask tests that require mocking."""

    def _mock_connect_to_db(app):
        """Connect the database to our Flask app."""

        # Configure to use our SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mock/wildally-mock.db'
        self.client = app
        db.init_app(self.client)


    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Mock session

        # Connect to mock database
        _mock_connect_to_db(app)

        def _mock_grab_image_dimensions(filename):
            return (920, 764)

        self._old_grab_image_dimensions = server.grab_image_dimensions
        server.grab_image_dimensions = _mock_grab_image_dimensions

        def _mock_generate_thumb(filename, crop_thumb):
            return None

        self._old_generate_thumb = server.generate_thumb
        server.generate_thumb = _mock_generate_thumb


    def tearDown(self):
        """Do at end of every test."""

        server.grab_image_dimensions = self._old_grab_image_dimensions
        server.generate_thumb = self._old_generate_thumb


    def test_crop_and_generate_thumb(self):

        assert server.THUMB_WIDTH == 200
        assert server.THUMB_HEIGHT == 175

        self.assertEqual(server.crop_and_generate_thumb("baby-chipmunk.jpg"), (23, 0, 897, 764))







        # with self.client as cli:
        #     assert flask.session['user_id'] == 5

        # assert server.UPLOAD_FOLDER == './mock/static/user/'

if __name__ == "__main__":
    import unittest

    unittest.main()