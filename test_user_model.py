"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()
        # app.config['TESTING']= True

    def tearDown(self):

        """Clean up anything in the session before next test."""
        res=super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual( repr(u), "<User #1: testuser, test@test.com>")

    def test_is_following(self):
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

        u1.following.append(u2)

        db.session.add(u1)
        db.session.add(u2)
        
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)

        u1.following.remove(u2)
        db.session.add(u1)

        db.session.commit()

        self.assertEqual(u1.is_following(u2), False)

    def test_is_followed_by(self):
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

        u2.following.append(u1)

        db.session.add(u1)
        db.session.add(u2)
        
        db.session.commit()

        self.assertEqual(u1.is_followed_by(u2), True)

        u2.following.remove(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u1.is_followed_by(u2), False)

    def test_signup(self):
        user1 = User.signup(
                username="Testuser",
                password="password",
                email="fakeemail@test.com",
                image_url="https://static.wikia.nocookie.net/heroes-and-villians/images/7/7e/Patrick_Star.png/revision/latest?cb=20180319192338",
            )

        db.session.add(user1)
        db.session.commit()

        self.assertIn(user1, User.query.all())
        self.assertEqual(user1.username, "Testuser")
        self.assertEqual(user1.email, "fakeemail@test.com")
        self.assertNotEqual(user1.password, "password")

        # Bcrypt strings should start with $2b$
        self.assertTrue(user1.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

        # user2 = User.signup(
        #         username="Testuser",
        #         password="password",
        #         email="fakeemail@test.com",
        #         image_url="https://static.wikia.nocookie.net/heroes-and-villians/images/7/7e/Patrick_Star.png/revision/latest?cb=20180319192338",
        #     )

        # db.session.add(user2)
        # db.session.commit()

        # self.assertRaises(IntegrityError)

        # self.assertNotIn(user2, User.query.all(), )
    
    def test_authenticate(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

        

    