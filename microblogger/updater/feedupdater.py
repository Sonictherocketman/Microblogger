""" Modifies the user's main feed.  """
from lxml import etree
from lxml.builder import E

from datetime.datetime import strptime

import time

from microblogger.post import post
from microblogger import util as u

def add_post(post):
    """ Adds the given post to the user's feed.  """
    tree = _get_user_feed('user/feed.xml')
    items = tree.XPath('//items')
    items.insert(0, post.to_element(post))
    u.write_user_feed(tree, 'user/feed.xml')


def fetch(start, n=20):
    """ Starting at the starting post id, fetches n posts (assuming the posts are ordered).
    Positive n for posts since start, negative n for previous posts. """

    # Get the tree, exract the starting point.
    tree = u.get_user_feed('user/feed.xml')
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

    tree = u.get_user_feed('user/feed.xml')
    stati = [post(status) for status in tree.XPath('//item[@guid]')]
    return stati[:n]


def delete_post(status_id):
    """ Deletes the post with the given id from the feed.  """
    tree = u.get_user_feed('user/feed.xml')
    for bad in tree.XPath('//item[@guid=$status_id]', status_id):
        bad.getparent().remove(bad)
    u.write_user_feed(tree, 'user/feed.xml')


def add_blocked_user(user_id, user_link, user_name):
    """ Adds a given user to the block list.  """
    # TODO


def add_follow_user(user_id, user_link, user_name):
    """ Adds a given user to the list of users to follow. """
    # TODO


def relocate_user_feed(url):
    """ Signals to the user's followers to discard the main feed
    redirect to the given URL. This will cause the user's current
    feed to be considered dead.

    Use with caution. """
    feed = u.get_user_feed('user/feed.xml')
    element = E.relocate(url)
    channel = feed.XPath('//channel')
    channel.append(element)
    u.write_user_feed(feed, 'user/feed.xml')





