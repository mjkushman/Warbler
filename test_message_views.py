"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User
from flask import g

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.drop_all()
    db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.session.rollback()
            User.query.delete()
            Message.query.delete()

            self.client = app.test_client()
            with self.client as c:
                with c.session_transaction() as sess:
                    self.testuser = User.signup(username="testuser",
                                                email="test@test.com",
                                                password="testuser",
                                                image_url=None)

                    db.session.commit()
                    sess[CURR_USER_KEY] = self.testuser.id
                    # print(self.testuser)

    def test_add_message(self):
        """Can user add a message?"""
        # with app.app_context():
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                print('self.testuser =', self.testuser)
                print('sess[CURR_USER_KEY] = ',sess[CURR_USER_KEY])
            # Now, that session setting is saved, so we can have
            # the rest of ours test
            # print(c.session_transaction())
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_homepage_view(self):
        """ Can client view homepage? """
        with self.client as c:
            resp = c.get('/')

            self.assertEqual(resp.status_code,200)


    def test_signup_view(self):
        """ Can client view the signup page? """
        with self.client as c:
            resp = c.get('/signup')

            self.assertEqual(resp.status_code,200)
            self.assertIn(b"username", resp.data) # Has the word "username" on page

    def test_signup_post(self):
        """ Can client successfully sign up a new user? """
        with self.client as c:
            resp = c.post('/signup', data={
                'username':'test1',
                'email': 'test1@test.com',
                'password': 'testpassword',
                'image_url':None
            })

            # Should redirect to / on success
            self.assertEqual(resp.status_code,302)
            self.assertEqual(resp.location,'/')


    def test_login_view(self):
        """ can the client view the login page?"""
        with self.client as c:
            resp = c.get('/login')
            self.assertEqual(resp.status_code,200)

            # check for form tag on page
            self.assertIn(b'</form>', resp.data)


    def test_login_post(self):
        """ Can the client successfully login? """
        # print('CLIENT', self.client)
        print('TEST USER', self.testuser)
        resp = self.client.post('/login', data={
            'username':self.testuser.username,
            'password':'testuser'
        })

        # Upon success, should 302 redirect to /
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location,'/')

        # After redirect client should see a page with username on it
        self.assertIn(b'test', resp.data)


