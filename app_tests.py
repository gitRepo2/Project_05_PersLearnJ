import unittest
import unittest.mock as mock

from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime

import learningApp
from models import User, LearningEntry

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, LearningEntry], safe=True)

USER_DATA = {
    'email': 'test_0@example.com',
    'password': 'password'
}


class UserModelTestCase(unittest.TestCase):
    """These methods test the learningApp. These test cases
    are copied and adapted from the tacocat challenge."""
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    email='test_1@example.com',
                    password='password'
                )


class LearningEntryModelTestCase(unittest.TestCase):
    def test_add_learning(self):
        with test_database(TEST_DB, (User, LearningEntry)):
            UserModelTestCase.create_users()
            user = User.select().get()
            LearningEntry.create(
                user=user,
                title='learn the ABC',
                learnt='nothing again',
                date='2019-11-01',
                time_spent='1',
                resourcesToRemember='this that',
                tags='elephant röseli'
            )
            entry = LearningEntry.select().get()

            self.assertEqual(LearningEntry.select().count(), 1)
            self.assertEqual(entry.user, user)


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        learningApp.app.config['TESTING'] = True
        learningApp.app.config['WTF_CSRF_ENABLED'] = False
        self.app = learningApp.app.test_client()


class UserViewsTestCase(ViewTestCase):
    def test_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/register', data=data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 200)

    def test_logout(self):
        with test_database(TEST_DB, (User,)):
            # Create and login the user
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)

            rv = self.app.get('/logout')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_logged_out_menu(self):
        rv = self.app.get('/')
        self.assertIn("login", rv.get_data(as_text=True).lower())

    def test_logged_in_menu(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)
            rv = self.app.get('/')
            self.assertIn("new entry", rv.get_data(as_text=True).lower())
            self.assertIn("log out", rv.get_data(as_text=True).lower())


class LearningViewsTestCase(ViewTestCase):
    def test_empty_db(self):
        with test_database(TEST_DB, (LearningEntry, User)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)
            rv = self.app.get('/')
            self.assertIn("journal is empty",
                          rv.get_data(as_text=True).lower())

    def test_add_learning(self):
        learning_data = {
            'title': 'learn the ABCD',
            'date': '2019-11-01',
            'time_spent': '1',
            'learnt': 'its load user not login user',
            'resourcesToRemember': 'this that',
            'tags': 'elephant röseli'
        }
        with test_database(TEST_DB, (User, LearningEntry)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)

            learning_data['user'] = User.select().get()
            rv = self.app.post('/new', data=learning_data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')
            self.assertEqual(LearningEntry.select().count(), 1)

    def test_learning_list(self):
        learning_data = {
            'title': 'learn the ABC',
            'date': '2019-11-01',
            'time_spent': '1',
            'learnt': 'so far',
            'resourcesToRemember': 'this that',
            'tags': 'elephant röseli'
        }
        with test_database(TEST_DB, (User, LearningEntry)):
            UserModelTestCase.create_users(1)
            learning_data['user'] = User.select().get()
            LearningEntry.create(**learning_data)
            self.app.post('/login', data=USER_DATA)
            rv = self.app.get('/')
            self.assertNotIn('Journal is empty', rv.get_data(as_text=True))
            self.assertIn(learning_data['title'],
                          rv.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
