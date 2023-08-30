"""User model tests."""

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


class UserModelTestCase(TestCase):
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
            u4 = User.signup('username4','email4@test.com','password4','/static/images/default-pic.png')
            
            db.session.add_all([u1,u2,u3,u4])
            db.session.commit()
            cls.client = app.test_client()

    
    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.session.rollback()
            User.query.delete()  # deletes all users
            Message.query.delete()  # deletes all messages
            Follows.query.delete()  # deletes all follows

            # u2 = User(email='test2@test.com', )

            

    def tearDown(self):
        """ Clean up any trash between tests """
        with app.app_context():
            db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            u4 = User(
                email="test4@test.com",
                username="testuser4",
                password="HASHED_PASSWORD"
            )

            db.session.add(u4)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u4.messages), 0)
            self.assertEqual(len(u4.followers), 0)
            
            # Should be able to look up user by email
            user4 = User.query.filter_by(email='test4@test.com').first()
            self.assertEqual(user4.username, 'testuser4')

    def test_user_follows(self):
        """ Test for user follow methods """
        with app.app_context():
            
            # Add a follow
            follow = Follows(user_being_followed_id=1, user_following_id=2)
            db.session.add(follow)
            db.session.commit()
            # get user 1 and user 2 and 3
            user1 = db.session.get(User, 1)
            user2 = db.session.get(User, 2)
            user3 = db.session.get(User, 3)

            # Does user2 follow user1?
            self.assertTrue(user1.is_followed_by(user2))
            self.assertTrue(user2.is_following(user1))

            # Does user1 follow user2?
            self.assertFalse(user2.is_followed_by(user1))
            self.assertFalse(user1.is_following(user2))

            # Does user1 follow user3?
            self.assertFalse(user3.is_followed_by(user1))
            self.assertFalse(user1.is_following(user3))

    def test_user_signup(self):
        """ Test user creation class method """
        
        with app.app_context():
            # # Can a user be created?
            user1 = User.signup('mytestuser', 'mytestuser@test.com','UNHASHED PASSWORD','/static/images/default-pic.png')
            db.session.commit()
            self.assertTrue(user1)


   
    def test_user_bad_signup(self):
        """ Test to make sure errors are thrown """
        with app.app_context():
            # Raise integrity error if none in nullable field
            with self.assertRaises(IntegrityError):
                user5 = User.signup('',None,'password','')
                db.session.commit()
            db.session.rollback()
         
            # Raise ValueError if password not provided
            with self.assertRaises(ValueError):
                user4 = User.signup('testtest4','test','','')
                db.session.commit()
            db.session.rollback()

            # Raise IntegrityError when trying to create a duplicate username?
            with self.assertRaises(IntegrityError):
                user2 = User.signup('mytestuser', 'mytestuser@test.com','UNHASHED PASSWORD','/static/images/default-pic.png')
                user3 = User.signup('mytestuser', 'mytestuser@test.com','UNHASHED PASSWORD','/static/images/default-pic.png')                
                db.session.commit()
            db.session.rollback()
            

    def test_user_authenticate(self):
        """ check for proper authentication method """
        with app.app_context():
            user = User.signup('username10','user10@test.com','password10','/static/images/default-pic.png')
            db.session.commit()
            # Expect successful login
            self.assertTrue(User.authenticate('username10','password10'))


    def test_user_bad_authenticate(self):
        """ Make sure authentication fails with incorrect credentils """
        
        with app.app_context():
            user = User.signup('username11','user11@test.com','password10','/static/images/default-pic.png')
            db.session.commit()
            # Expect failed login
            self.assertFalse(User.authenticate('username11','wrongpass'))


    def test_user_repr(self):
        """ Test __repr__ method """
        with app.app_context():

            # User repr method            
            user1 = User.query.filter_by(email='test1@test.com').first()
            self.assertIn('testuser1', user1.__repr__())

            user2 = User.query.filter_by(email='test2@test.com').first()
            self.assertIn('testuser2', user2.__repr__())