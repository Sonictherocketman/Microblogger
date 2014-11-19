# -*- coding: utf-8 -*-
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

from feed import feedgenerator as fg, feedupdater as fu

# Configuration
DEBUG = True
SECRET_KEY = 'find some secret key.'
CACHE = '/tmp/microblogger_cache.json'
SETTINGS = '/tmp/microblogger_settings.json'
ROOT_DIR = '/var/www/microblogger/'


# Admin and setup


def init_cache():
    """ Do the initial cache setup. This function
    passes if a cache already exists. To clear it,
    delete the cache file. """
    if not os.path.isfile(CACHE):
        cache = {[]}
        with open(CACHE, 'w') as f:
            f.write(json.dumps(cache))


def init_settings():
    """ Do the initial settings setup. This function
    passes if a settings file already exists.

    WARNING: Do not delete the settings file. There
    will be no way for you to log into your account
    once this file is deleted. """
    if not os.path.isfile(SETTINGS):
        settings = {[]}
        with open(SETTINGS, 'w') as f:
            f.write(json.dumps(settings))


def from_cache(key):
    """ Fetches values from the cache. """
    if os.path.isfile(CACHE):
        with open(CACHE, 'r') as f:
            cache = json.loads(f.read())
            if key in cache.keys():
                return cache[key]


def from_settings(key):
    """ Fetches values from the cache. """
    if os.path.isfile(CACHE):
        with open(SETTINGS, 'r') as f:
            settings = json.loads(f.read())
            if key in settings.keys():
                return cache[key]


# Site pages


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = from_settings(session['user_id'])


@app.route('/')
def home():
    """ Shows the user's timeline or if no user is logged in it
    will redirect to the user's public timeline (their most
    recent posts) for public viewing. """
    if not g.user:
        return redirect(url_for('user_timeline'))
    return render_template('timeline.html', messages=fu.fetch()


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ POST Creates the new user. GET Displays the reg page."""
    if g.user:
        return redirect(url_for('home'))

    if request.method == 'POST':
        error = None
        # TODO: Registration logic
        if registration_successful:
            session['user_id'] = user['user_id']
            return redirect(url_for('home'))
        else:
            return render_template('registration.html', error=error)
    else:
        return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ POST will log the user in then take them to their timeline.
    GET will display the login page. """
    if g.user:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # TODO Login logic.
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """ POST will log the user out then takes them to the homepage.
    GET will display the logout page. """
    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('home'))
    else:
        render_template('logout.html')


@app.route('/<user_id>')
def user_timeline(user_id):
    """ Shows the user's public timeline (their most
    recent posts). This is the only timeline view that
    an unauthenticated user can see. """
    return render_template('public_timeline.html', messages=fu.fetch())


@app.route('/<user_id>/<post_id>')
def individual_post(post_id):
    """ Displays an individual post in it's own page. """
    # TODO Add call to feedupdater for fetching individual posts.
    return render_template('individual_post.html', messages=fu.fetch(post_id))


# REST APIs


@app.route('/api/timeline/home_timeline/', methods=['GET'])
def home_timeline():
    """ Returns the 100 most recent posts in the
    user's home timeline. """
    # TODO Get timeline


@app.route('/api/timeline/user_timeline/', methods=['GET'])
def user_timeline():
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
   # Init the application
    app = Flask(__name__)
    app.config.from_object(__name__)
    os.chdir(ROOT_DIR)
    init_cache()
    init_settings()

    # Startup
    app.run()


