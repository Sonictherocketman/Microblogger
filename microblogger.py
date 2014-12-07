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
# - Reorganize the utilities methods to the util class.



from flask import Flask, request, session, url_for, redirect,\
    render_template, abort, g
from werkzeug import check_password_hash, generate_password_hash

import os
import re
from threading import Thread

from feed import feedgenerator as fg,\
        feedreader as fr, \
        feedupdater as fu
from crawler.crawler import MicroblogFeedCrawler
from util import init_cache, init_settings, to_settings,\
        from_settings, from_cache

from datetime import datetime


# Configuration
DEBUG = True
CACHE = '/tmp/microblogger_cache.json'
# TODO Remove this file from the tmp dir since IT IS TEMPORARY!
SETTINGS = '/tmp/microblogger_settings.json'
ROOT_DIR = '/var/www/microblogger/'


# Init the application
app = Flask(__name__)
app.config.from_object(__name__)
crawler = MicroblogFeedCrawler(fr.get_user_follows_links())


# Site pages


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = from_settings(SETTINGS, session['user_id'])
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
    elif from_settings(SETTINGS, 'username') is not None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        error = ''

        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        email = request.form['email']

        if from_settings(SETTINGS, 'username') is not None:
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
            to_settings(SETTINGS, 'username', username)
            to_settings(SETTINGS, 'pwd_hash', generate_password_hash(password))
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
        error = ''
        username = request.form['username']
        password = request.form['password']
        pwd_hash = from_settings(SETTINGS, 'pwd_hash')
        if from_settings(SETTINGS, 'username') != username:
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


@app.route('/status/<post_id>')
def individual_post(post_id):
    """ Displays an individual post in it's own page. """
    return render_template('individual_post.html', messages=fu.fetch(post_id))


@app.route('/post', methods=['POST'])
def add_post():
    """ Adds a new post to the feed. """
    if 'user_id' not in session:
        abort(401)

    print 'Inserting post'
    print request.form['post-text']
    fu.add_post({
        'description': request.form['post-text'],
        'pubdate': datetime.now(),
        'guid': os.urandom(10).encode('base-64'),
        'language': fr.get_user_language()
    })
    print 'inserted'
    return redirect(url_for('home'))


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


@app.route('/api/status/add', methods=['POST'])
def api_add_post():
    """ Adds a new post to the user's feed. """
    if g.user:
        fu.add_post({
            'description': request.args['description'],
            'pubdate': now(),
            'guid': os.urandom(10).encode('base-64'),
            'language': request.args['language'] or fr.get_user_language()
          })


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
    init_cache(CACHE)
    init_settings(SETTINGS)

    # Create a secret key
    to_settings(SETTINGS, 'secret', os.urandom(64).encode('base-64'))
    app.secret_key = from_settings(SETTINGS, 'secret')

    # Start the crawler on another thread.
    crawler_task = Thread(target=crawler.start, name='crawler')
    crawler_task.setDaemon(True)
    crawler_task.start()

    # Start up the app
    app.run()

