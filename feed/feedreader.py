# -*- coding: utf-8 -*-
""" Reads values from the user's feed. """

from lxml import etree

import util as u


# User Functions


def get_username():
    """ Gets the user's chosen username from
    the user feed.  """
    feed = u.get_user_feed('user/feed.xml')
    return feed.xpath('//username')[0].text


def get_user_bio():
    """ Gets the user's chosen bio. """
    feed = u.get_user_feed('user/feed.xml')
    return feed.xpath('//channel/description')[0].text


def get_user_id():
    """ Gets the user's id. """
    feed = u.get_user_feed('user/feed.xml')
    return feed.xpath('//channel/user_id')[0].text


def get_user_full_name():
    """ Gets the user's chosen full name. """
    feed = u.get_user_feed('user/feed.xml')
    return feed.xpath('//channel/user_full_name')[0].text


def get_user_link():
    """ Gets the user's feed link. """
    feed = u.get_user_feed('user/feed.xml')
    return feed.xpath('//channel/link')[0].text


def get_user():
    """ Gets all the details of the user. """
    user = {
            'username': get_username(),
            'user_link': get_user_link(),
            'bio': get_user_bio(),
            'user_id': get_user_id(),
            'user_full_name': get_user_full_name()
            }
    return user


# Follows/Blocks Functions


# TODO


# Status Functions


def fetch(start, n=0):
    """ Starting at the starting post id, fetches n posts (assuming the posts are ordered).
    Positive n for posts since start, negative n for previous posts.
    Zero (or nothing) for only the post with the given id. """

    # Get the tree, exract the starting point.
    tree = u.get_user_feed('user/feed.xml')
    stati = [post(status) for status in tree.xpath('//channel/item[@guid]')]

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
    stati = [post(status) for status in tree.xpath('//item')]
    return stati[:n]


