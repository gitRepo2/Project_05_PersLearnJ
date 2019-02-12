import dateutil
import regex
from flask import (Flask, g, render_template, flash, redirect, url_for)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from unidecode import unidecode
import pep8

import forms
import models
from models import LearningEntry


DEBUG = True
PORT = 5003
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh,,q345lkqjed0adh3ououea.auoub!'

models.initialize()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Load the user in the login process"""
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """It registers (or signs up) a user"""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        flash("Yay, you registered!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Login method that redirects to login for unsuccessful login or
    to index after a successful login."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=False)
                flash("You've been logged in with {}!".format(user.email), "success")
                return redirect(url_for('index'))  # current_user is new.
            else:
                flash("You've not been logged in!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """It log out the user"""
    logout_user()  # deletes the cookie
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.route('/')
@login_required
def index():
    """Landing page where the user learing entries are shown if logged in"""
    learnings = LearningEntry.select().where(models.LearningEntry.user==
        g.user._get_current_object()).order_by(LearningEntry.date.desc())\
        .limit(100)
    return render_template('index.html', learnings=learnings)


@app.route('/details/<string:timestamp>')
def details(timestamp):
    """Selects a entry to be displayed on the details page."""
    timestamp = dateutil.parser.parse(timestamp)
    learning = LearningEntry.select().\
        where(LearningEntry.timestamp_of_entry ==timestamp)
    return render_template('details.html', learning=learning[0])


@app.route('/entries/<string:tag>')
@login_required
def tagged_entries(tag):
    """Shows journal entries filtered by a tag."""
    learnings = LearningEntry.select().where(
        LearningEntry.tags.contains(tag) and
        models.LearningEntry.user==g.user._get_current_object())
    return render_template('index.html', learnings=learnings)


@app.route('/new', methods=('GET', 'POST'))
def new():
    """Page to enter a new journal entry."""
    form = forms.LearningForm()
    if form.validate_on_submit():
        flash("Yay, you added a learning!", "success")
        models.LearningEntry.add_learning(
            user=g.user._get_current_object(),
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learnt=form.learnt.data,
            resourcesToRemember=form.resourcesToRemember.data,
            tags=slugify(form.tags.data)
        )
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/edit/<string:timestamp>', methods=('GET', 'POST'))
def edit(timestamp):
    """Method to edit a existing journal entry."""
    timestamp = dateutil.parser.parse(timestamp)
    l_entry = LearningEntry.select().where(LearningEntry.timestamp_of_entry == timestamp)
    form = forms.LearningForm(obj=l_entry[0])
    if form.validate_on_submit():
        flash("Yay, you updated a learning!", "success")
        models.LearningEntry.edit_learning(
            timestamp=timestamp,
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learnt=form.learnt.data,
            resourcesToRemember=form.resourcesToRemember.data,
            tags=slugify(form.tags.data)
        )
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, learning=l_entry[0])


@app.route('/entries/delete/<string:timestamp>')
def delete(timestamp):
    """Deletes a journal entry."""
    timestamp = dateutil.parser.parse(timestamp)
    learning = LearningEntry.select().where(LearningEntry.timestamp_of_entry == timestamp)
    learning[0].delete_instance()
    return redirect(url_for('index'))


@app.route('/entry')
def entry():
    pass


@app.template_filter()
def split_string(text, delimiter=' '):
    """This method splits the string into single strings"""
    return text.split(delimiter)


def slugify(text, delimiter=u' '):
    """This method turns text into human readable keywords.
    Source: http://flask.pocoo.org/snippets/5/"""
    _punct_re = regex.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    mylist = []
    for word in _punct_re.split(text.lower()):
        mylist.extend(unidecode(word).split())
    return str(delimiter.join(mylist))


@app.template_filter('slugify')
def _slugify(string):
    """This method slugifies a string argument from the html page"""
    if not string:
        return ""
    else:
        return slugify(string)


if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)

checker = pep8.Checker('learningApp.py')
checker.check_all()
