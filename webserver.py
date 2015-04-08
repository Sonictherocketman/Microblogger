""" The web-api server. """

import os
import uuid
import re
from datetime import datetime
import signal
import sys
import pytz
from functools import wraps

from flask import Flask, request, session, url_for, redirect,\
    render_template, abort
from werkzeug import check_password_hash, generate_password_hash
from flask_limiter import Limiter

from feed import feedgenerator as fg,\
        feedreader as fr, \
        feedupdater as fu
from crawler.crawler import MicroblogFeedCrawler, OnDemandCrawler
from cachemanager import CacheManager
from settingsmanager import SettingsManager


# Init the application
app = Flask(__name__)
limiter = Limiter(app)
main_crawler = None
on_demand_crawler = None
app.debug = True
app.secret_key = SettingsManager.get('secret')
CacheManager(cache_location=SettingsManager.get('cache_location'))

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('error.log')
    file_handler.setLevel(logging.WARNING)
    from logging import Formatter
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
            ))
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


####################################################################
########################### URL Mappings ###########################
####################################################################

# Home

@app.route('/', methods=['GET'])
def home():
    """ Shows the user's timeline or if no user is logged in it
    will redirect to the user's public timeline (their most
    recent posts) for public viewing. """
    posts = []
    user = fr.get_user()
    if 'user_id' in session:
        posts = CacheManager.get_timeline()
    else:
        posts = fr.fetch_top()
        for post in posts:
            post['user'] = user
    return render_template('timeline.html', posts=posts, user=user)


# Login/Registration


@app.route('/register', methods=['GET'])
def get_register():
    """ Displays the reg page."""
    if 'user_id' in session:
        return redirect(url_for('home'))
    elif SettingsManager.get('username') is not None:
        return redirect(url_for('get_login'))
    else:
        return render_template('registration.html')


@app.route('/register', methods=['POST'])
def post_register():
    """ Registers a new user. """
    if 'user_id' in session:
        return redirect(url_for('home'))
    elif SettingsManager.get('username') is not None:
        return redirect(url_for('login'))

    error = ''
    user_full_name = request.form['full_name']
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    email = request.form['email']

    if SettingsManager.get('username') is not None:
        return redirect(url_for('login'))
    elif username is None:
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
        # Generate the new feed.
        fg.generate_new_feed()
        fg.generate_new_block_list()
        fg.generate_new_follows_list()

        # Update the feed.
        fg.set_username(username)
        fg.set_user_full_name(user_full_name)

        # Update the settings.
        SettingsManager.add('username', username)
        SettingsManager.add('pwd_hash', generate_password_hash(password))
        session['user_id'] = username
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
    pwd_hash = SettingsManager.get('pwd_hash')
    if SettingsManager.get('username') != username:
        error = 'Invalid username'
    elif not check_password_hash(pwd_hash, password):
        error = 'Invalid password'
    else:
        session['user_id'] = username
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
    return render_template('account.html', user=fr.get_user())


@app.route('/account', methods=['POST'])
@login_required
def post_account():
    # Flask apparently throws 400 errors if POST form data isn't present.
    # Full name
    if request.form.get('full_name_changed') == 'true':
        user_full_name = request.form['full_name']
        fg.set_user_full_name(user_full_name)
    # Username
    if request.form.get('username_changed') == 'true':
        username = request.form['username']
        fg.set_username(username)
    # Bio
    if request.form.get('bio_changed') == 'true':
        bio = request.form['bio']
        fg.set_user_description(bio)
    # Email
    if request.form.get('email_changed') == 'true':
        email = request.form['email']
        SettingsManager.add('email', email)
    # Password
    if request.form.get('password_changed') == 'true':
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if password == password_confirm:
            SettingsManager.add(generate_password_hash(password))
    # Relocate [WARNING]
    if request.form.get('relocate_changed') == 'true':
        relocate_url = request.form['relocate_url']
        fu.relocate_user_feed(relocate_url)
    # Language
    if request.form.get('language_changed') == 'true':
        language = request.form['language']
        # TODO: Add language change function to fu.
    return render_template('account.html', user=fr.get_user(), error='Your settings have been saved.')


# Browsing


@app.route('/<user_id>/profile', methods=['GET'])
@login_required
def get_user_profile(user_id):
    """ Get the profile of the given user."""
    # TODO Cache this
    user = None
    posts = []
    user_link = [u['user_link'] for u in fr.get_user_follows()
            if u['user_id'] == user_id]

    # Go get the posts for that given user.
    on_demand_crawler = OnDemandCrawler()
    data = on_demand_crawler.get_all_items(user_link)
    posts = data[user_link[0]]
    user = posts[0]['user']

    return render_template('timeline.html', user=user, posts=posts)


@app.route('/<user_id>/follows', methods=['GET'])
@login_required
def get_user_follows(user_id):
    """ Display a list of the users that a given user follows. """
    if user_id == fr.get_user_id():
        user = fr.get_user()
        follow = fr.get_user_follows()
    else:
        # TODO: Call the on_demand_crawler to fetch a
        # list of the follows that a remote user has.
        pass
    return render_template('follows.html', user=user, follows=follows)


@app.route('/<user_id>/blocks', methods=['GET'])
@login_required
def get_user_blocks(user_id):
    """ Display a list of the users that a given user has blocked. """
    if user_id == fr.get_user_id():
        user = fr.get_user()
        blocks = fr.get_user_blocks()
    else:
        # TODO: Call the on_demand_crawler to fetch a
        # list of the follows that a remote user has.
        pass
    return render_template('blocks', user=user, blocks=blocks)


@app.route('/<user_id>/<status_id>', methods=['GET'])
@login_required
def get_status_by_user(user_id, status_id):
    """ Get a given status by a given user. """
    # TODO: Test this...
    user = None
    post = None

    if user_id == fr.get_user_id():
        user = fr.get_user()
        post = fr.fetch(status_id)
    else:
        user_link = [u['user_link'] for u in fr.get_user_follows()
                if u['user_id'] == user_id]

        # Go get the posts for that given user.
        data = on_demand_crawler.get_all_items(user_link)
        info = data[user_link[0]]['info']
        items = data[user_link[0]]['items']
        user = {
                'username': info['user_name'],
                'user_id': info['user_id'],
                'user_link': info['user_link'],
                'bio': info['description'],
                'user_full_name': info['user_full_name']
                }

        def find_and_package_item(items):
            """ Go over the list of items and package them for display. """
            # Try to find the one post needed.
            for item in items:
                if item['guid'] == status_id:
                    return {
                        'description': item['description'],
                        'puddate_str': item['pubdate_str']
                        }
            return None

        post = find_and_package_item(items)

        # If not found, then search their whole feed.
        if post is None:
            data = on_demand_crawler.get_all_items(user_link)
            items = data[user_link[0]]['items']
            post = find_and_package_items(items)

    return render_template('individual_post.html', user=user, post=post)


# Status and Profile Handlers
# TODO REFACTOR

@app.route('/new_status', methods=['POST'])
@login_required
@limiter.limit('100 per 15 minute')
def add_status():
    """ Adds a new post to the feed. """
    if len(request.form['post-text']) > 200:
        return redirect(url_for('home', error='Too many characters'))

    fu.add_post({
        'description': request.form['post-text'],
        'pubdate': datetime.now(pytz.utc),
        'guid': str(uuid.uuid4().int),
        'language': fr.get_user_language()
    })
    return redirect(url_for('home'))


@app.route('/add_follow', methods=['POST'])
@login_required
@limiter.limit('50 per 15 minutes')
def add_follow():
    """ Adds a new follow to the user's list. """
    user_link = request.form['follow-url']
    print user_link
    # Using the link given by the user, tell the
    # crawler to get the rest of the info.
    user_info = OnDemandCrawler().get_all_items([user_link])

    user_name = user_info[user_link]['info']['username']
    user_id = user_info[user_link]['info']['user_id']

    fu.add_follow_user(user_id=user_id, user_name=user_name, user_link=user_link)
    return redirect(url_for('home'))


# XML File Getters
# TODO: Remove these in production. Have apache do the static file hosting.


@app.route('/feed', methods=['GET'])
def feed():
    """ This just returns the user's XML feed. """
    with open('user/feed.xml') as f:
        return f.read()


@app.route('/blocks', methods=['GET'])
def blocks():
    """ Returns the user's block list. """
    with open('user/blocks.xml') as f:
        return f.read()


@app.route('/follows', methods=['GET'])
def follows():
    """ Returns the user's block list. """
    with open('user/follows.xml') as f:
        return f.read()


# Internals


@app.route('/messages', methods=['GET'])
def get_messages():
    """ Used by the crawler to get all the recent messages
    posted to the server. """
    # TODO
    pass

@app.route('/messages', methods=['POST'])
def post_messages():
    """ Public URL, written in the User's feed for sending
    newly posted messages to the registered users. """
    # TODO
    pass



if __name__ == '__main__':
    # Start up the app
    print 'Hi. This is debug mode.'
    app.run()

