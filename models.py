import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

import pytz
from peewee import *
import dateutil.parser
import pep8


DATABASE = SqliteDatabase('learnings.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)  # for creating a list view of all users

    @classmethod
    def create_user(cls, email, password, is_admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=is_admin)
        except IntegrityError:
            raise ValueError("User already exists")


class LearningEntry(Model):
    user = ForeignKeyField(rel_model=User)
    timestamp_of_entry = DateTimeField(default=datetime.datetime.now)
    title = TextField()
    learnt = TextField()
    date = DateField()
    time_spent = IntegerField()
    resourcesToRemember = TextField()
    tags = CharField(default="")

    class Meta:
        database = DATABASE

    @classmethod
    def add_learning(cls, user, title, learnt, date,
                     time_spent, resourcesToRemember, tags):
        """This method adds a learning entry into the database."""
        try:
            LearningEntry.create(
                user=user,
                title=title,
                learnt=learnt,
                date=date,
                time_spent=time_spent,  # in minutes
                resourcesToRemember=resourcesToRemember,
                tags=tags)
        except Exception as e:
            print("Error. A learning entry could not be written to the "
                  "database because {}.".format(e))

    @classmethod
    def edit_learning(cls, timestamp, title, learnt, date,
                      time_spent, resourcesToRemember, tags):
        """This method updates a learning entry in he database."""
        try:
            q = (LearningEntry.update(
                title=title,
                learnt=learnt,
                date=date,
                time_spent=time_spent,  # in minutes
                resourcesToRemember=resourcesToRemember,
                tags=tags).\
                where(LearningEntry.timestamp_of_entry == timestamp))
            no = q.execute()
            print('Number of entries updated: ', no)
        except Exception as e:
            print("Error. A learning entry could not be updated to the "
                  "database because {}.".format(e))


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, LearningEntry], safe=True)
    DATABASE.close()


checker = pep8.Checker('models.py')
checker.check_all()
