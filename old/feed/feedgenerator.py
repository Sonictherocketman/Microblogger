# -*- coding: utf-8 -*-
""" Creates the base user feed, and sets the initial values. """

import post
import util as u

from lxml.builder import E
from lxml.etree import CDATA


# Generate new feeds.


def generate_new_feed(location='user/feed.xml', username='', user_ud='',):
    """ Creates a blank XML feed and writes it. To fill in the
    information for the feed use the other helper methods provided. """
    feed = E.channel(
            E.username(''),
            E.user_id(''),
            E.user_full_name(''),
            E.description(CDATA('')),
            E.link(''),
            E.blocks('', count=''),
            E.follows('', count=''),
            E.docs(''),
            E.language(''),
            E.lastBuildDate(''),
            E.reply_to(
                E.link(''),
                E.reply_to_user_id(''),
                E.reply_to_status_id(),
                E.reply_from_user_id(),
                E.reply_status_id(),
                E.user_link()
                ),
            )
    u.write_user_feed(feed, location)


def generate_new_block_list(rel_location='user/blocks.xml'):
    """ Creates a new root block list in
    the default location.

    Warning: Does not migrate old lists. """
    feed = E.channel(
                E.username(''),
                E.user_id(''),
                E.link(''),
                E.next_node(''),
                E.lastBuildDate(''),
                count='0'
                )
    u.write_user_feed(feed, location)


def generate_new_follows_list(rel_location='user/follows.xml'):
    """ Creates a new root follows list in
    the default location.

    Warning: Does not migrate old lists. """
    feed = E.channel(
            E.username(''),
            E.user_id(''),
            E.link(''),
            E.next_node(''),
            E.lastBuildDate(''),
            count='0'
            )
    u.write_user_feed(feed, location)


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


    def get_user_language():
        """ Gets the user's chosen default language. """
        feed = u.get_user_feed('user/feed.xml')
        return feed.xpath('//channel/language')[0].text



    def set_username(username):
        """ Sets the username for a user's feed. This does not traverse
        all past nodes. The username in those files is left untouched. """
        feed = u.get_user_feed('user/feed.xml')
        element = feed.xpath('//channel/username')
        if element:
            element[0].text = username
        u.write_user_feed(feed, 'user/feed.xml')


    def set_user_full_name(full_username):
        """ Sets the user's full name. Does not traverse all past nodes.
        Previous feed files are untouched. """
        feed = u.get_user_feed('user/feed.xml')
        element = feed.xpath('//channel/user_full_name')
        if element:
            element[0].text = full_username
        u.write_user_feed(feed, 'user/feed.xml')


    def set_user_description(description):
        """ Sets the user's description (bio) information. Past feed
        nodes are untouched. """
        feed = u.get_user_feed('user/feed.xml')
        element = feed.xpath('//chanel/description')
        if element:
            element[0].text = description
        u.write_user_feed(feed, 'user/feed.xml')


    def set_default_language(language):
        """ Sets the user's default language. Past feed nodes are unaffected. """
        feed = u.get_user_feed('user/feed.xml')
        element = feed.xpath('//chanel/language')
        if element:
            element[0].text = language
        u.write_user_feed(feed, 'user/feed.xml')


    def set_reply_to(reply_to_user_id, url=''):
        """ Sets the reply_to information into the feed. If no reply_to_user_id is
        provided, the feed's user_id is used, if found. If not, raise
        InformationNotProvidedError. Past feed nodes are unaffected. """
        feed = u.get_user_feed('user/feed.xml')
        reply_to_user_id_element = feed.xpath('/channel/reply_to/reply_to_user_id')
        if reply_to_user_id_element:
            if reply_to_user_id is None:
                reply_to_user_id = feed.xpath('/channel/user_id')[0].text
            reply_to_user_id_element[0].text = reply_to_user_id

        reply_to_link_element = feed.xpath('/channel/reply_to/link')
        if reply_to_link_element:
            reply_to_link_element[0].text = url

        u.write_user_feed(feed, 'user/feed.xml')


    def set_docs_url(url):
        """ Sets the documentation url for the feed. Past feed
        nodes are unaffected. """
        feed = u.get_user_feed('user/feed.xml')
        reply_to_user_element = feed.xpath('/channel/docs')
        if element:
            element[0].text = username
        u.write_user_feed(feed, 'user/feed.xml')


# Set blocks list values.


    def set_blocks_url(url):
        """ Sets the url for the user's block list. """
        feed = u.get_user_feed('user/blocks.xml')
        reply_to_user_element = feed.xpath('/channel/link')
        if element:
            element[0].text = username
        u.write_user_feed(feed, 'user/blocks.xml')


# Set follows list values.


    def set_follows_url(url):
        """ Sets the url for the user's following list. """
        feed = u.get_user_feed('user/follows.xml')
        reply_to_user_element = feed.xpath('/channel/link')
        if element:
            element[0].text = username
        u.write_user_feed(feed, 'user/follows.xml')


