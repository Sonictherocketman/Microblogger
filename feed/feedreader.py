# -*- coding: utf-8 -*-
""" Reads values from the user's feed. """

from lxml import etree

import util as u

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
