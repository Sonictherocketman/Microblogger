# -*- coding: utf-8 -*-
#!/usr/local/bin/python
""" The web-api server.

Running this will start the server, do initial setup
and get your new microblog up and running.

:license: MIT, see LICENSE for more information.

Alter the values in the 'configuration' section to fit
your needs.

The expected layout is:
    www/
        microblogger/
            user/
                feed.xml
                blocks.xml
                follows.xml
"""


# TODO
# - Add rate limiting.


from flask import Flask, request, session, url_for, redirect,\
    render_template, abort, g
from werkzeug import check_password_hash, generate_password_hash

import os
import json
import re

from feed import feedgenerator as fg, feedupdater as fu
from crawler import feedreader as fr, crawler

# Configuration
DEBUG = True
CACHE = '/tmp/microblogger_cache.json'
SETTINGS = '/tmp/microblogger_settings.json'
ROOT_DIR = '/var/www/microblogger/'


# Init the application
app = Flask(__name__)
app.config.from_object(__name__)


# Admin and setup


def init_cache():
    """ Do the initial cache setup. This function
    passes if a cache already exists. To clear it,
    delete the cache file. """
    if not os.path.isfile(CACHE):
        cache = {}
        with open(CACHE, 'w') as f:
            f.write(json.dumps(cache))


def init_settings():
    """ Do the initial settings setup. This function
    passes if a settings file already exists.

    WARNING: Do not delete the settings file. There
    will be no way for you to log into your account
    once this file is deleted. """
    if not os.path.isfile(SETTINGS):
        settings = {}
        with open(SETTINGS, 'w') as f:
            f.write(json.dumps(settings))


def from_cache(key):
    """ Fetches a value from the cache. """
    if os.path.isfile(CACHE):
        with open(CACHE, 'r') as f:
            cache = json.loads(f.read())
            if key in cache.keys():
                return cache[key]


def to_cache(key, value):
    """ Adds a value to the cache. """
    if os.path.isfile(CACHE):
        with open(CACHE, 'r+') as f:
                current_settings = json.loads(f.read())
                current_settings[key] = value
                f.seek(0)
                f.write(json.dumps(current_settings))
                f.truncate()


def add_post_to_cache(post):
    """ Adds a post to the cache. """
    cached_posts = from_cache('posts')
    cached_posts.append(post)
    to_cahce('posts', cached_posts)


def from_settings(key):
    """ Fetches a value from the settings. """
    if os.path.isfile(SETTINGS):
        with open(SETTINGS, 'r') as f:
            settings = json.loads(f.read())
            if key in settings.keys():
                return settings[key]


def to_settings(key, value):
    """ Adds a value to the settings file. """
    if os.path.isfile(SETTINGS):
        with open(SETTINGS, 'r+') as f:
                current_settings = json.loads(f.read())
                current_settings[key] = value
                f.seek(0)
                f.write(json.dumps(current_settings))
                f.truncate()


# Site pages


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = from_settings(session['user_id'])
        print 'user_authenticated'


@app.route('/')
def home():
    """ Shows the user's timeline or if no user is logged in it
    will redirect to the user's public timeline (their most
    recent posts) for public viewing. """
    posts = []
    user = fr.get_user()
    if g.user is None:
        posts = fu.fetch_top()
    else:
        posts = fr.get_posts()
    return render_template('timeline.html', posts=posts, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ POST Creates the new user. GET Displays the reg page."""
    if g.user:
        return redirect(url_for('home'))
    elif from_settings('username') is not None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        error = ''

        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']

        if from_settings('username') is not None:
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
            to_settings('username', username)
            to_settings('pwd_hash', generate_password_hash(password))
            session['user_id'] = username
            return redirect(url_for('home'))

        return render_template('registration.html', error=error)
    else:
        return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ POST will log the user in then take them to their timeline.
    GET will display the login page. """
    if g.user:
        return redirect(url_for('home'))
    # Check login info.
    error = ''
    if request.method == 'POST':
        # TODO Login logic.
        error = ''
        username = request.form['username']
        password = request.form['password']
        pwd_hash = from_settings('pwd_hash')
        if from_settings('username') != username:
            error = 'Invalid username'
        elif not check_password_hash(pwd_hash, password):
            error = 'Invalid password'
        else:
            session['user_id'] = username
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """ POST will log the user out then takes them to the homepage.
    GET will display the logout page. """
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/<post_id>')
def individual_post(post_id):
    """ Displays an individual post in it's own page. """
    return render_template('individual_post.html', messages=fu.fetch(post_id))


# REST APIs


@app.route('/api/timeline/home_timeline', methods=['GET'])
def api_home_timeline():
    """ Returns the 100 most recent posts in the
    user's home timeline. """
    # TODO Get timeline
    print 'Hi. You\'ve reached the user timeline.'


@app.route('/api/timeline/user_timeline', methods=['GET'])
def api_user_timeline():
    """ Returns the 100 most recent posts in the
    timeline of the user indicated. If no user is
    indicated, then the authenticated user is used.

    :params: user_id, user_link, username

    All three parameters are desired though if a
    unique match is found, not all elements may
    be required or used. """
    user_id = request.args.get('user_id')
    user_link = request.args.get('user_link')
    username = request.args.get('username')
    # TODO Get posts.


# TODO APIs
# - Get posts before/after <post_id>
# - Get post with <post_id>
# - Add post
# - Delete post
# - Repost
# - Reply
# - Follow <user_id>, <user_link>, <username>
# - Unfollow <user_id>, <user_link>, <username>
# - Block <user_id>, <user_link>, <username>
# - Unblock <user_id>, <user_link>, <username>
# - Get list of follows
# - Get list of blocks
# - PROBABLY NOT IN v1: Get list of follows who follow you (friends)



# Main


if __name__ == '__main__':
    init_cache()
    init_settings()

    # Create a secret key
    to_settings('secret', os.urandom(64).encode('base-64'))
    app.secret_key = from_settings('secret')

    # Start the crawler
    crawler.crawl(callback=lambda post: add_post_to_cache(post))

    # Start up the app
    app.run()

