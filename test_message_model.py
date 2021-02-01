"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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

class MessageModelTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.uid = 1
        u = User.signup("testuser", "fakeemail@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):

        res = super().tearDown()
        db.session.rollback()
        return res


    def test_message_model(self):
        message=Message(
            text="This is a test message", 
            user_id=self.uid)

        db.session.add(message)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual( self.u.messages[0].text, "This is a test message")

    def test_likes_model(self):

        message1=Message(
            text="This is a test message", 
            user_id=self.uid)

        message2=Message(
            text="Testing another msg", 
            user_id=self.uid)

        new_user= User.signup("another1", "blah@test.com", "password", None)
        new_user_id=2
        new_user.id=new_user_id

        db.session.add_all([message1, message2, new_user])
        db.session.commit()

        new_user.likes.append(message1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == new_user_id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, message1.id)

