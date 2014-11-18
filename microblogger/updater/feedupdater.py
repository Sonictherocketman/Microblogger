""" Modifies the user's main feed.  """
from lxml import etree
from lxml.builder import E

from datetime.datetime import strptime

import time

from microblogger.post import post

def add_post(post):
    """ Adds the given post to the user's feed.  """
    tree = _get_user_feed('user/feed.xml')
    items = tree.XPath('//items')
    items.insert(0, post.to_element(post))
    _write_user_feed(tree, 'user/feed.xml')

def fetch(start, n=20):
    """ Starting at the starting post id, fetches n posts (assuming the posts are ordered).
    Positive n for posts since start, negative n for previous posts. """

    # Get the tree, exract the starting point.
    tree = _get_user_feed('user/feed.xml')
    stati = [post(status) for status in tree.XPath('//item[@guid]')]

    starting = stati.index([status for status in stati if status['guid'] == start][0])

    # Get n posts.
    if len(stati[starting:]) < abs(n):
        if n > 0:
            return stati[:starting]
        if n < 0:
            return stati[starting:]
    return stati[starting:n]


def fetch_top(n=20):
    """ Fetches the n most recent posts in reverse chronological order.  """
    if n < 0:
        raise IndexError

    tree = _get_user_feed('user/feed.xml')
    stati = [post(status) for status in tree.XPath('//item[@guid]')]
    return stati[:n]

def delete_post(status_id):
    """ Deletes the post with the given id from the feed.  """
    tree = _get_user_feed('user/feed.xml')
    for bad in tree.XPath('//item[@guid=$status_id]', status_id):
        bad.getparent().remove(bad)
    _write_user_feed(tree, 'user/feed.xml')

def _get_user_feed(rel_location):
    """ Get the etree representation of the feed located at the rel_location.  """
    tree = None
    with open(rel_location, 'r') as f:
        data = f.read()
        tree = etree.parse(StringIO(data))
    return tree

def _write_user_feed(tree, rel_location)
    """ Write the etree representation of the feed to the rel_locaiton.  """
    with open(rel_location, 'w') as f:
        tree.write(f)





