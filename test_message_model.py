""" Message Model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import NotNullViolation

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.drop_all()
    db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """ create some users in the db """
        with app.app_context():
            
            u1 = User(
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD"
            )
            u2 = User(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD"
            )
            u3 = User(
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD"
            )
            
            db.session.add_all([u1,u2,u3])
            db.session.commit()
            cls.client = app.test_client()

    
    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.session.rollback()
            User.query.delete()  # deletes all users
            Message.query.delete()  # deletes all messages
            Follows.query.delete()  # deletes all follows
            

    def tearDown(self):
        """ Clean up any trash between tests """
        with app.app_context():
            db.session.rollback()


    def test_message_model(self):
        """Does basic model work?"""
        with app.app_context():
            text = "Test Message Hello World"
            message = Message(
                text=text,
                user_id=1
            )
            db.session.add(message)
            db.session.commit()

            user = db.session.get(User, 1)
            
            # The message text and user_id should have saved correctly
            self.assertEqual(message.text,text)
            self.assertEqual(message.user_id,1)


    def test_message_timestamp(self):
        """Does the message have a timestamp? """
        with app.app_context():
            text = "Test Message Hello World"
            message = Message(
                text=text,
                user_id=1
            )
            db.session.add(message)
            db.session.commit()

            user = db.session.get(User, 1)
            
            # The message should have a timestamp
            self.assertTrue(message.timestamp)


    def test_message_relationship(self):
        """Is a message properly associated with user? """
        with app.app_context():
            text = "Test Message Hello World"
            message = Message(
                text=text,
                user_id=1
            )
            db.session.add(message)
            db.session.commit()

            user = db.session.get(User, 1)
            
            # User 1 should have morie than 0 messages 
            self.assertGreater(len(user.messages), 0)

            # Test the relationship to User model
            self.assertEqual(message.user.username, 'testuser1')