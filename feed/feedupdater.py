# -*- coding: utf-8 -*-
""" Modifies the user's main feed.  """

from lxml import etree
from lxml.builder import E

import time

from post import post, to_element
import util as u
from settingsmanager import SettingsManager


def _write_to_feed(tree, rel_location):
    """ Writes the given tree to the location given. If pagination
    is required, then it will paginate the files. Wraps
    u.write_user_feed() """
    # Check if the feed is too big. If so, make a new
    # feed and insert it there.
    size = u.get_user_feed_size(rel_locaiton)
    if size > SettingsManager.get('max_feed_size_bytes') \
            or count > SettingsManager.get('max_posts_per_feed'):
        old_feed_name = u.archive_user_feed(rel_location)
        from lxml.builder import E
        tree.xpath('//channel')[0].append(E.next_node(old_filename))
    u.write_user_feed(tree, rel_location)


def _search_recurs(rel_location, xpath_qry):
    """ Searches the tree representation of the given file for
    any item that meets the query string. If not found, it searches
    the `next_node` until it succeeds or no more `next_nodes` are
    found.

    Returns a tuple (rel_file_url, guid)
    """
    feed = u.get_user_feed(starting_location)
    item = feed.xpath(xpath_qry)
    next_node = feed.xpath('//next_node')

    if item:
        return rel_location, post(item[0])['guid']
    elif next_node:
        new_rel_location = u.convert_url(next_node[0].text, to_relative=True)
        _search_recurs(new_rel_location, xpath_qry)
    else:
        return


def add_post(new_post):
    """ Adds the given post to the user's feed. """
    tree = u.get_user_feed('user/feed.xml')
    channel = tree.xpath('//channel')[0]
    channel.append(to_element(new_post))
    _write_to_feed(tree, 'user/feed.xml')


def delete_post(status_id):
    """ Deletes the post with the given id from the feed.  """
    # TODO: Test
    to_delete_qry = '/channel/items/item[@guid={0}'.format(status_id)

    feed_url, guid = _search_recurs('user/feed.xml', to_delete_qry)

    tree = u.get_user_feed(feed_url)
    item = tree.xpath('//item[@guid=$guid]', guid)
    item.getparent().remove(bad)

    u.write_user_feed(tree, 'user/feed.xml')


def add_blocked_user(user_id, user_link, user_name):
    """ Adds a given user to the block list.  """
    feed = u.get_user_feed('user/blocks.xml')
    tree = feed.xpath('/channel/items')
    element = E.item(
            E.user_id(user_id),
            E.user_name(user_name),
            E.user_link(user_link)
            )
    tree.append(element)
    _write_to_feed(feed, 'user/blocks.xml')


def add_follow_user(user_id, user_link, user_name):
    """ Adds a given user to the list of users to follow. """
    feed = u.get_user_feed('user/follows.xml')
    tree = feed.xpath('/channel/items')
    element = E.item(
            E.user_id(user_id),
            E.user_name(user_name),
            E.user_link(user_link)
            )
    tree.append(element)
    _write_to_feed(feed, 'user/follows.xml')


def delete_follow_user(user_id, user_link, user_name):
    """ Deletes a user from the user's follow list. All 3 parameters
    are needed since the user_id and user_name may not be unique. """
    # TODO: Test
    to_delete_qry = '/channel/items/item[@user_name={0} and @user_id={1} \
            and @user_link={2}]'.format(user_name, user_id, user_link)

    feed_url, guid = _search_recurs('user/follows.xml', to_delete_qry)

    tree = u.get_user_feed(feed_url)
    item = tree.xpath('//item[@guid=$guid]', guid)
    item.getparent().remove(bad)

    u.write_user_feed(tree, 'user/follows.xml')


def relocate_user_feed(url):
    """ Signals to the user's followers to discard the main feed
    redirect to the given URL. This will cause the user's current
    feed to be considered dead.

    Use with caution. """
    feed = u.get_user_feed('user/feed.xml')
    element = E.relocate(url)
    channel = feed.xpath('//channel')
    channel.append(element)
    _write_to_feed(feed, 'user/feed.xml')

