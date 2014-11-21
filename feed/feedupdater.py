# -*- coding: utf-8 -*-
""" Modifies the user's main feed.  """

from lxml import etree
from lxml.builder import E

from datetime.datetime import strptime

import time

from .. import post
from .. import util as u


def add_post(new_post):
    """ Adds the given post to the user's feed. """
    tree = _get_user_feed('user/feed.xml')
    items = tree.XPath('//items')
    items.insert(0, post.to_element(new_post))
    u.write_user_feed(tree, 'user/feed.xml')


def fetch(start, n=0):
    """ Starting at the starting post id, fetches n posts (assuming the posts are ordered).
    Positive n for posts since start, negative n for previous posts.
    Zero (or nothing) for only the post with the given id. """

    # Get the tree, exract the starting point.
    tree = u.get_user_feed('user/feed.xml')
    stati = [post(status) for status in tree.XPath('/channel/item[@guid]')]

    starting = stati.index([status for status in stati if status['guid'] == start][0])

    # Get only the single post.
    if n == 0:
        return starting
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
    stati = [post(status) for status in tree.XPath('/channel/item[@guid]')]
    return stati[:n]


def delete_post(status_id):
    """ Deletes the post with the given id from the feed.  """
    tree = u.get_user_feed('user/feed.xml')
    for bad in tree.XPath('/channel/items/item[@guid=$status_id]', status_id):
        bad.getparent().remove(bad)
    u.write_user_feed(tree, 'user/feed.xml')


def add_blocked_user(user_id, user_link, user_name):
    """ Adds a given user to the block list.  """
    feed = u.get_user_feed('user/blocks.xml')
    tree = feed.XPath('/channel/items')
    element = E.item(
            E.user_id(user_id),
            E.user_name(user_name),
            E.user_link(user_link)
            )
    tree.append(element)
    u.write_user_feed(feed, 'user/blocks.xml')


def add_follow_user(user_id, user_link, user_name):
    """ Adds a given user to the list of users to follow. """
    feed = u.get_user_feed('user/follows.xml')
    tree = feed.XPath('/channel/items')
    element = E.item(
            E.user_id(user_id),
            E.user_name(user_name),
            E.user_link(user_link)
            )
    tree.append(element)
    u.write_user_feed(feed, 'user/follows.xml')


def delete_follow_user(user_id, user_link, user_name):
    """ Deletes a user from the user's follow list. All 3 parameters
    are needed since the user_id and user_name may not be unique. """
    feed = u.fet_user_feed('user/follows.xml')
    for bad in feed.XPath('/channel/items/item[@user_name=$user_name \
            and @user_id=$user_name and @user_link=$user_link]',
            user_name=user_name, user_id=user_id, user_link=user_link)
        bad.parent().remove(bad)
    u.write_user_feed(feed, 'user/follows.xml')


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






