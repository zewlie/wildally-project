import json
from unittest import TestCase
from model import User, Org, Pickup, Hour, OrgAnimal, Animal, ContactType, Phone, Email, SiteType, Site, Click, ClickFilter, connect_to_db, db, sample_data
from server import app
from datetime import datetime
import flask
import server
import tasks

class WildAllyUnitTestCase(TestCase):
    """Discrete code testing."""

    def test_account_setting_type(self):
        self.assertEqual(server.account_setting_type("address"), 'address')
        self.assertEqual(server.account_setting_type("org-email"), 'org')
        self.assertEqual(server.account_setting_type("email"), 'user')

    def test_allowed_file(self):
        self.assertEqual(server.allowed_file("image.png"), True)
        self.assertEqual(server.allowed_file("image.pdf"), False)


class FlaskRouteTests(TestCase):
    """Flask tests for routes."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

    def test_create_account_invalid_JSON(self):
        """Test status code 405 from improper JSON on post to raw"""
        response = self.client.post('/user-added', data="not json", content_type='application/json')
        self.assertEqual(response.status_code, 500)


class MockFlaskTests(TestCase):
    """Flask tests that require mocking."""


    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Mock session

        # Connect to temporary database
        connect_to_db(app, "sqlite:///")

        # Create tables and add sample data
        db.create_all()
        sample_data()


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


    def test_gather_clicks(self):

        self.assertEqual(server.gather_clicks(5, ["volunteer"]), (1, "volunteer"))



    def test_load_click_info_from_db(self):

        self.assertEqual(len(server.load_click_info_from_db()), 4)
        self.assertEqual(server.load_click_info_from_db()[2][0].id, 1)
        self.assertEqual(server.load_click_info_from_db()[3][0].id, 1)


    def test_update_analytics(self):

        self.assertNotEqual(server.update_analytics()['day'], {})
        self.assertNotEqual(server.update_analytics()['day']['hour1'], [])
        self.assertNotEqual(server.update_analytics()['week'], {})
        self.assertNotEqual(server.update_analytics()['week']['day1'], [])
        self.assertNotEqual(server.update_analytics()['month'], {})
        self.assertNotEqual(server.update_analytics()['month']['week1'], [])
        self.assertIsNotNone(server.update_analytics()['filters'])
        self.assertIsNotNone(server.update_analytics()['allfilters'])

    def test_create_account(self):

        response = self.client.post('/user-added', data=dict(
                                    username='TestOrg',
                                    website='testorg.com', 
                                    is_org='yes',
                                    address1='425 N 5th St',
                                    address2='Suite 1',
                                    phone='555-555-5555',
                                    password='password',
                                    desc='desc',
                                    city='Phoenix',
                                    show_address='0',
                                    zipcode='85004',
                                    org_email='testorg@testorg.com',
                                    state='AZ',
                                    email='testorg@gmail.com',
                                    org_name='Test Org',
                                    ein='123456789'
                                    ), follow_redirects=True)

        self.assertIn('Test Org', response.data)
        self.assertIn('testorg@testorg.com', response.data)
        self.assertIn('425 N 5th St', response.data)
        self.assertIn('85004', response.data)
        self.assertEqual(response.status_code, 200)

        # with self.client as cli:
        #     assert flask.session['user_id'] == 5

        # assert server.UPLOAD_FOLDER == './mock/static/user/'

if __name__ == "__main__":
    import unittest

    unittest.main()