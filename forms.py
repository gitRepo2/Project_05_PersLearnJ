from flask_wtf import FlaskForm, validators
from wtforms import StringField, PasswordField, TextAreaField, DateField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Email, Length, EqualTo)
import pep8

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
        )


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class LearningForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[
            DataRequired()
        ])
    date = DateField(
        'Date',
        format='%Y-%m-%d',
        validators=[
            DataRequired()
        ])
    time_spent = StringField(
        'Time spent in hours',
        validators=[
            DataRequired(),
            Regexp(
                r'^[0-9]',
                message=("Key in numbers only.")
            )
        ])
    learnt = StringField(
        'What I learnt',
        validators=[
            DataRequired()
        ]
    )
    resourcesToRemember = StringField(
        'Resources to remember',
        validators=[
            DataRequired()
        ]
    )
    tags = StringField(
        'Add some tags',
        validators=[
            DataRequired()
        ]
    )


checker = pep8.Checker('forms.py')
checker.check_all()
