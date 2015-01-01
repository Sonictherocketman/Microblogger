# -*- coding: utf-8 -*-
""" Utilities for doing basic feed file IO.  """

from lxml import etree
import os
import json


# Util Functions

def convert_url(url, to_relative=False, to_absolute=False):
    # TODO: Test
    """ Converts a local xml url between relative and absolute forms.
    Ex:
        url = 'http://sample.tld/user/feed.xml'
        print convert_url(url, to_relative=True)
        >>> 'user/feed.xml'

        url = 'user/feed.xml'
        print convert_url(url, to_absolute=True)
        >>> 'http://sample.tld/user/feed.xml'
    """
    if to_relative:
        return re.search(string=url, pattern=r'(user/(feed|follows|blocks|archive)(/.+)?\.xml)').group(0)
    elif to_absolute:
        return SettingsManager.get('domain') + url
    else:
        print 'No conversion output selected.'
        raise ValueError


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


def get_user_feed_size(rel_location):
    """ Returns the size, in bytes, of the given feed. """
    return os.path.getsize(rel_location)


def archive_user_feed(src):
    """ Moves the current user feed to the archive directory.
    Returns the relative file name of the old file. """
    import shutil as s, datetime.datetime.now as now, re
    m = re.search(string=filename, pattern=r'.+/(.+)\.(xml|XML)')
    orig_filename = m.group(0)

    filename = 'user/archive/{0}_{1}.xml'.format(orig_filename, now().strftime('%Y%m%d_%H%M%S'))
    s.copy2(src, filename)
    return filename


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
                f.write(json.dumps(current_cache,
                    sort_keys=True,
                    indent=4))
                f.truncate()


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
                f.write(json.dumps(current_settings,
                    sort_keys=True,
                    indent=4))
                f.truncate()


