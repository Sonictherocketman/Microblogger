# -*- coding: utf-8 -*-
""" Utilities for doing basic feed file IO.  """

from lxml import etree
import os
import json

# TODO
# - Add pagination support for reading and writing.

# User Feed Stuff


def get_user_feed(rel_location):
    """ Get the etree representation of the feed located at the rel_location.  """
    tree = None
    with open(rel_location, 'r') as f:
        tree = etree.parse(f)
    return tree


def write_user_feed(tree, rel_location):
    """ Write the etree representation of the feed to the rel_locaiton.  """
    with open(rel_location, 'w') as f:
        tree.write(f, pretty_print=True)


# Cache and Settings Init


def init_cache(cache):
    """ Do the initial cache setup. This function
    passes if a cache already exists. To clear it,
    delete the cache file. """
    if not os.path.isfile(cache):
        cache_data = {}
        with open(cache, 'w') as f:
            f.write(json.dumps(cache_data))


def init_settings(settings):
    """ Do the initial settings setup. This function
    passes if a settings file already exists.

    WARNING: Do not delete the settings file. There
    will be no way for you to log into your account
    once this file is deleted. """
    if not os.path.isfile(settings):
        settings_data = {}
        with open(settings, 'w') as f:
            f.write(json.dumps(settings_data))


# Cache Methods


def from_cache(cache, key):
    """ Fetches a value from the cache. """
    if os.path.isfile(cache):
        with open(cache, 'r') as f:
            cache_data = json.loads(f.read())
            if key in cache_data.keys():
                return cache_data[key]


def to_cache(cache, key, value):
    """ Adds a value to the cache. """
    if os.path.isfile(cache):
        with open(cache, 'r+') as f:
                current_cache = json.loads(f.read())
                current_cache[key] = value
                f.seek(0)
                f.write(json.dumps(current_cache))
                f.truncate()


def add_post_to_cache(post, cache):
    """ Adds a post to the cache. """
    cached_posts = from_cache(cache, 'posts')
    cached_posts.append(post)
    to_cache(cache, 'posts', cached_posts)


# Settings Methods


def from_settings(settings, key):
    """ Fetches a value from the settings. """
    if os.path.isfile(settings):
        with open(settings, 'r') as f:
            settings_data = json.loads(f.read())
            if key in settings_data.keys():
                return settings_data[key]


def to_settings(settings, key, value):
    """ Adds a value to the settings file. """
    if os.path.isfile(settings):
        with open(settings, 'r+') as f:
                current_settings = json.loads(f.read())
                current_settings[key] = value
                f.seek(0)
                f.write(json.dumps(current_settings))
                f.truncate()


