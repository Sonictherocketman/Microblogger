""" The web-api server. """

import os
import re
from datetime import datetime
import signal
import sys
import pytz
from uuid import uuid4
from functools import wraps

from flask import Flask, request, session, url_for, redirect,\
    render_template, abort
from werkzeug import check_password_hash, generate_password_hash
from flask_limiter import Limiter

from cachemanager import CacheManager
from settingsmanager import SettingsManager as settings
from model.user import User
from model.status import Status

# Init the application
app = Flask(__name__)
limiter = Limiter(app)
app.debug = True
app.secret_key = settings.get('secret')
CacheManager(cache_location=settings.get('cache_location'))

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('error.log')
    file_handler.setLevel(logging.WARNING)
    from logging import Formatter
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    for handler in app.logger.handlers:
        limiter.logger.addHandler(handler)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('get_login'))
        return f(*args, **kwargs)
    return decorated_function


def user_for_username(username):
    for _, user_dict in settings.get('registered_users').iteritems():
        if user_dict['username'] == username:
            return user_dict


####################################################################
########################### URL Mappings ###########################
####################################################################

# Home

@app.route('/', methods=['GET'])
def home():
    """ Shows the user's timeline or if no user is logged in it
    will redirect to the user's public timeline (their most
    recent posts) for public viewing. """
    # Not logged in and multi-user mode.
    if 'user_id' not in session and not settings.get('single_user_mode'):
        return render_template('welcome.html')
    # Not logged in and single-user mode.
    elif 'user_id' not in session and settings.get('single_user_mode'):
        user_id = settings.get('single_user_id')
        username = settings.get_user(user_id)['username']
        return redirect(url_for('get_user_profile', username=username))
    # Logged in
    elif 'user_id' in session:
        user_id = session['user_id']
    # Single-user mode, but no user yet.
    elif settings.get('single_user_mode') and settings.get('single_user_id') is None:
        return redirect(url_for('get_register'))
    # Single-user mode, user exists.
    else:
        user_id = settings.get('single_user_id')
    link = settings.get('registered_users').get(user_id).get('feed_location')
    user = User(local_url=link)
    posts = user.home_timeline()
    return render_template('timeline.html', posts=posts, user=user, page_type='timeline')


# Login/Registration


@app.route('/register', methods=['GET'])
def get_register():
    """ Displays the reg page."""
    if 'user_id' in session:
        return redirect(url_for('home'))
    elif settings.get('single_user_id') is not None:
        return redirect(url_for('get_login'))
    else:
        return render_template('registration.html')


@app.route('/register', methods=['POST'])
def post_register():
    """ Registers a new user. """
    error = ''
    user_full_name = request.form['full_name']
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    email = request.form['email']

    # User is already logged in.
    if 'user_id' in session:
        return redirect(url_for('home'))
    # No more users can register.
    elif settings.get('single_user_mode') \
            and len(settings.get('registered_users')) > 0:
        error = 'No more users can register at this time.'
    # Username is alredy registered.
    users = settings.get('registered_users')
    username_taken = True if \
            len([uid for uid, ud, in users.iteritems() if ud.get('username') == username]) > 0 \
            else False
    if username_taken:
        return redirect(url_for('get_login'))

    # Register the new user.
    if username is None:
        error = 'No username provided.'
    elif len(username) < 8 or len(username) > 25:
        error = 'Username is not the correct length. \
                Please enter a username between 8-25 characters.'
    elif re.search('[^a-zA-Z0-9\_]', username) is not None:
        error = 'Usernames can only contain letters an numbers.'
    elif re.search('\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', email) is not None:
        error = 'Please enter a valid email address.'
    elif password is None or password_confirm is None:
        error = 'You must fill in your password.'
    elif password != request.form['password_confirm']:
        error = 'Passwords do not match.'
    elif len(password) < 8 or re.search('[a-zA-Z0-9]', password) is None:
        error = 'Your password must be at least 8 characters long and \
                must be a combination of numbers and letters. Special\
                characters are allowed and encouraged.'
    else:
        new_user, feed_location, blocks_location, follows_location = User.create(username)

        if settings.get('single_user_mode'):
            settings.add('single_user_id', new_user.user_id)

        domain = settings.get('domain')
        new_user.profile = 'http://{0}/{1}'.format(domain, new_user.username)
        new_user.link = 'http://{0}/{1}/feed.xml'.format(domain, new_user.username)
        new_user.follows_url = 'http://{0}/{1}/follows.xml'.format(domain, new_user.username)
        new_user.blocks_url = 'http://{0}/{1}/blocks.xml'.format(domain, new_user.username)
        new_user.message_url = 'http://{0}/{1}/message.'.format(domain, new_user.username)
        new_user.language = 'en'

        # Update the settings.
        pwd_hash = generate_password_hash(password)
        settings.add_user(username=new_user.username,
                pwd_hash=pwd_hash,
                user_id=new_user.user_id,
                feed_location=feed_location,
                blocks_location=blocks_location,
                follows_location=follows_location)
        session['user_id'] = new_user.user_id
        return redirect(url_for('home'))

    return render_template('registration.html', error=error)


@app.route('/login', methods=['GET'])
def get_login():
    """ Display the login page if they aren't already logged in. """
    if 'user_id' in session:
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='')


@app.route('/login', methods=['POST'])
def do_login():
    """ Logs the user in. """
    error = ''
    username = request.form['username']
    password = request.form['password']
    username_and_ids = { ud['username']: uid for uid, ud in settings.get('registered_users').iteritems() }

    if username not in username_and_ids.keys():
        error = 'Invalid username'

    pwd_hash =  settings.get_user(username_and_ids[username]).get('pwd_hash')
    if not check_password_hash(pwd_hash, password):
        error = 'Invalid password'
    else:
        session['user_id'] = username_and_ids[username]
        return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """ Logs the user out. """
    session.pop('user_id', None)
    return redirect(url_for('home'))


# Account Management


# TODO This still doesn't work
@app.route('/account', methods=['GET'])
@login_required
def get_account():
    """ Allows the user to make changes to their profile. """
    user_id = session['user_id']
    location = settings.get_user(user_id)['feed_location']
    user = User(local_url=location)
    return render_template('account.html', user=user)


@app.route('/account', methods=['POST'])
@login_required
def post_account():
    # Flask apparently throws 400 errors if POST form data isn't present.
    # Full name
    user_id = session['user_id']
    location = settings.get_user(user_id)['feed_location']
    user = User(local_url=location)

    if request.form.get('full_name_changed') == 'true':
        user.full_name = request.form['full_name']
    # Username
    if request.form.get('username_changed') == 'true':
        username= request.form['username']
        if len(username) > 0:
            user.username = username
    # Bio
    if request.form.get('bio_changed') == 'true':
        user.description = request.form['bio']
    # Email
    if request.form.get('email_changed') == 'true':
        email = request.form['email']
        user_dict = settings.get_user(user_id)
        user_dict['email'] = email
        settings.add_user(user_dict)
    # Password
    if request.form.get('password_changed') == 'true':
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if password == password_confirm:
            user_dict = settings.get_user(user_id)
            user_dict['pwd_hash'] = generate_password_hash(password)
            settings.add_user(user_dict)
    # Language
    if request.form.get('language_changed') == 'true':
        user.language = request.form['language']
    return render_template('account.html', user=user, error='Your settings have been saved.')


# Browsing


@app.route('/<username>', methods=['GET'])
def get_user_profile(username):
    """ Get the profile of the given user."""
    user = None
    user_dict = user_for_username(username)
    if user_dict is not None:
        user = User(local_url=user_dict['feed_location'])
    else:
        # User is remote.
        # TODO
        pass
    return render_template('timeline.html', user=user, posts=user.user_timeline(), page_type='profile')


@app.route('/<username>/follows', methods=['GET'])
def get_user_follows(username):
    """ Display a list of the users that a given user follows. """
    user = None
    user_dict = user_for_username(username)
    if user_dict is not None:
        user = User(local_url=user_dict['feed_location'])
    else:
        # User is remote.
        # TODO
        pass
    return render_template('follows.html', user=user, follows=user.follows, page_type='following')


@app.route('/<username>/blocks', methods=['GET'])
def get_user_blocks(username):
    """ Display a list of the users that a given user has blocked. """
    user = None
    user_dict = user_for_username(username)
    if user_dict is not None:
        user = User(local_url=user_dict['feed_location'])
    else:
        # User is remote.
        # TODO
        pass
    return render_template('blocks', user=user, blocks=user.blocks)


@app.route('/<username>/<status_id>', methods=['GET'])
@login_required
def get_user_status(username, status_id):
    """ Get a given status by a given user. """
    user = None
    user_dict = user_for_username(username)
    if user_dict is not None:
        user = User(local_url=user_dict['feed_location'])
    else:
        # TODO
        pass
    posts = user.user_timeline()
    posts = [post for post in posts if post.guid == status_id]
    if len(posts) > 0:
        post = posts[0]
        return render_template('individual_post.html', user=user, post=post)
    else:
        # TODO 404
        pass


@app.route('/<username>/status/<status_id>/reply', methods=['POST'])
def post_reply(username, status_id):
    """ Accepts incoming replies on behalf of users and queues them.
    Returns 201 if created properly, or 403 if not allowed.
    """
    # TODO
    pass


# Private Messages


@app.route('/<username>/message', methods=['GET'])
def get_messages():
    """ Retrieves the list of private messages for a given user.
    If the user in question is not logged in, returns 401.
    """
    # TODO
    pass

@app.route('/<username>/message', methods=['POST'])
def post_messages():
    """ Accepts incoming messages from the public on behalf of
    a user. Adds those messages to the database and returns 201
    if accepted, or 403 if not allowed.
    """
    # TODO
    pass


# Status and Profile Handlers
# TODO REFACTOR


@app.route('/add_status', methods=['POST'])
@login_required
@limiter.limit('100 per 15 minute')
def post_status():
    """ Adds a new post to the feed. """
    status_text = request.form['post-text'].strip()
    user_id = session['user_id']
    if len(status_text) > 200:
        return redirect(url_for('home', error='Too many characters'))
    elif status_text == '':
        return redirect(url_for('home', error='Post cannot be empty'))
    user_dict = settings.get_user(user_id)
    if user_dict is not None:
        user = User(local_url=user_dict['feed_location'])
        guid = uuid4().hex[-12:]
        reply_url = '{0}/status/{1}/reply'.format(user.profile, guid)
        status = Status({
            'description': status_text,
            'pubdate': datetime.now(pytz.UTC),
            'guid': guid,
            'reply': reply_url
            })
        user.add_post(status)
    return redirect(url_for('home'))


@app.route('/follow', methods=['POST'])
@login_required
@limiter.limit('50 per 15 minutes')
def post_follow():
    """ Adds a new follow to the user's list. """
    user_link = request.form['follow-url']
    if user_link != '':
        user_id = session.get('user_id')
        user_dict = settings.get_user(user_id)
        user = User(local_url=user_dict['feed_location'])
        user.follow(user_link=user_link)
    return redirect(url_for('home'))


@app.route('/unfollow', methods=['POST'])
@login_required
@limiter.limit('50 per 15 minutes')
def post_unfollow():
    """ Unfollows a given user. """
    user_link = request.form['user_link']
    username = request.form['username']
    user_id = request.form['user_id']

    my_user_id = session.get('user_id')
    user_dict = settings.get_user(my_user_id)
    user = User(local_url=user_dict['feed_location'])
    user.unfollow(user_link=user_link, user_name=username, user_id=user_id)
    return redirect(url_for('home'))


@app.route('/block', methods=['POST'])
@login_required
@limiter.limit('50 per 15 minutes')
def post_follow():
    """ Adds a new follow to the user's list. """
    user_link = request.form['follow-url']
    if user_link != '':
        user_id = session.get('user_id')
        user_dict = settings.get_user(user_id)
        user = User(local_url=user_dict['feed_location'])
        user.block(user_link=user_link)
    return redirect(url_for('home'))


@app.route('/unblock', methods=['POST'])
@login_required
@limiter.limit('50 per 15 minutes')
def post_unfollow():
    """ Unfollows a given user. """
    user_link = request.form['user_link']
    username = request.form['username']
    user_id = request.form['user_id']

    my_user_id = session.get('user_id')
    user_dict = settings.get_user(my_user_id)
    user = User(local_url=user_dict['feed_location'])
    user.unblock(user_link=user_link, user_name=username, user_id=user_id)
    return redirect(url_for('home'))


# XML File Getters


@app.route('/<username>/feed.xml', methods=['GET'])
def feed(username):
    """ This just returns the user's XML feed. """
    location = user_for_username(username)['feed_location']
    with open(location) as f:
        return f.read()


@app.route('/<username>/blocks.xml', methods=['GET'])
def blocks(username):
    """ Returns the user's block list. """
    location = user_for_username(username)['blocks_location']
    with open(location) as f:
        return f.read()


@app.route('/<username>/follows.xml', methods=['GET'])
def follows(username):
    """ Returns the user's block list. """
    location = user_for_username(username)['follows_location']
    with open(location) as f:
        return f.read()





if __name__ == '__main__':
    # Start up the app
    app.run(threaded=True)


