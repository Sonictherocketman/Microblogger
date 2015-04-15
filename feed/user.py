""" Feed related operations. """

import time

from lxml.builder import E
from lxml.etree import CDATA
from lxml import etree
from dateutil.parser import parse

import post
import util as u
from settingsmanager import SettingsManager


# Misc Utilities


def _get_from_feed(rel_location, xpath):
    """ Gets a given attr from the feed at the location. """
    feed = u.get_user_feed(rel_location)
    return feed.xpath(xpath)[0].text


def _set_to_feed(rel_location, xpath, value):
    """ Sets a value to the node at the xpath in the file given. """
    feed = u.get_user_feed(rel_location)
    element = feed.xpath(xpath)
    if element:
        element[0].text = value
    u.write_user_feed(feed, rel_location)


def _write_to_feed(tree, rel_location):
    """ Writes the given tree to the location given. If pagination
    is required, then it will paginate the files. Wraps
    u.write_user_feed() """
    # Check if the feed is too big. If so, make a new
    # feed and insert it there.
    size = u.get_user_feed_size(rel_location)
    count = len(tree.xpath('//item'))
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


def _enum(**enums):
    return type('Enum', (), enums)


# User Model


DataLocations = _enum(
        LOCAL=0,
        CACHED=1,
        REMOTE=2
        )


class NoSuchUserError(Exception):
    pass


class RemoteUserPropertyError(Exception):
    pass

class User(object):
    """ A representation of a given microblog user.

    The User class models all kinds of users independent of their relation
    to the system. That means that users who are members of the system, those
    who are not, and those who are temporarily cached are all handled by this
    class.

    Users are given a status (LOCAL, REMOTE, or CACHED) to represent their
    relation to the system. Their propertied are handled according to that
    status.

    Users can move between these statuses based on certain critera (subject to
    optimization). However, users who are managed by the system will always be
    LOCAL users. REMOTE users may become CACHED under certain conditions and
    CACHED users may revert to REMOTE status if unused for a period.

    @since 2015-04-15 ONLY LOCAL AND CACHED USERS ARE SUPPORTED
    """

    def __init__(self, local_url=None, remote_url=None, entries=None):
        if isinstance(entries, dict):
            """ Create new User from dict. """
            self._status = DataLocations.CACHED
            self.__dict__.update(**entries)
        elif isinstance(local_url, str):
            """ Create new local User with feed @ location. """
            self._status = DataLocations.LOCAL
            self._rel_location = local_url
        elif isinstance(remote_url, str):
            """ Create new remote user with feed @ location. """
            self._status = DataLocations.REMOTE
            self._feed_url = remote_url

    def _generate_new_user_feed(location='user/feed.xml', username='', user_ud='',):
        """ Creates a blank XML feed and writes it. To fill in the
        information for the feed use the other helper methods provided. """
        # TODO: Combine the 3 methods.
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


    def _generate_new_block_list(rel_location='user/blocks.xml'):
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

    def _generate_new_follows_list(rel_location='user/follows.xml'):
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

    ############# Behind the Curtain ##############

    def _get_attr(self, attr, xpath):
        """ Fetches the given attr based on the user's status. """
        if self._status == DataLocations.LOCAL:
            return _get_from_feed(self._rel_location, xpath)
        elif self._status == DataLocations.REMOTE:
            # TODO Implement Crawler Backed Attrs
            pass
        else:
            return self.__dict__.get(attr)

    def _set_attr(self, attr, xpath, value):
        """ Sets the given attr to the value. If the user is NOT a
        local user, then that user's cached values are updated. """
        if self._status == DataLocations.LOCAL:
            _set_to_feed(self._rel_location, xpath, value)
        elif self._status == DataLocations.REMOTE:
            raise RemoteUserPropertyError
        else:
            self.__dict__[attr] = value

    ############# Properties ##############

    @property
    def username(self):
        return self._get_attr('username', '//channel/username')

    @username.setter
    def username(self, username):
        self._set_attr('username', '//channel/username', username)

    @property
    def description(self):
        return self._get_attr('description', '//channel/description')

    @description.setter
    def description(self, description):
        self._set_attr('description', '//channel/description', description)

    @property
    def user_id(self):
        return self._get_attr('user_id', '//channel/user_id')

    @user_id.setter
    def user_id(self, user_id):
        self._set_attr('user_id', '//channel/user_id', user_id)

    @property
    def full_name(self):
        return self._get_attr('user_full_name', '//channel/user_full_name')

    @full_name.setter
    def full_name(self, full_name):
        self._set_attr('user_full_name', '//channel/user_full_name', full_name)

    @property
    def link(self):
        return self._get_attr('link', '//channel/link')

    @link.setter
    def link(self, link):
        self._set_attr('link', '//channel/link', link)

    @property
    def language(self):
        return self._get_attr('language', '//channel/language')

    @language.setter
    def language(self, language):
        self._set_attr('language', '//channel/language', language)

    @property
    def follows(self):
        """ Get the list of the people the user follows. """
        # TODO: FIX THIS - This only works for LOCAL users.
        feed = u.get_user_feed('user/follows.xml')
        follows = []
        follows_el = feed.xpath('//channel/item')
        s4
        if not len(follows_el) > 0:
            return list()

        for user_el in follows_el:
            user_dict = post._recursive_dict(user_el)[1]
            follows.append(User(**user_dict))
        return follows

    @property
    def follows_just_links(self):
        """ Gets the list of links to the feeds the user follows.
        Basically a simplified version of get_user_follows. """
        return [user.link for user in self.follows]

    @property
    def follows_url(self):
        return self._get_attr('follows', '//channel/follows')

    @follows_url.setter
    def follows_url(self, url):
        self._set_attr('follows', '//channel/follows', url)

    @property
    def blocks(self):
        # TODO FIX THIS - This only works for LOCAL users.
        """ Get the list of the people the user follows. """
        feed = u.get_user_feed('user/blocks.xml')
        blocks = []
        blocks_el = feed.xpath('//channel/item')

        for user_el in blocks_el:
            user_dict = post._recursive_dict(user_el)[1]
            blocks.append(User(**user_dict))
        return blocks

    @property
    def blocks_just_links(self):
        return [user.link for user in self.blocks]

    @property
    def blocks_url(self):
        return self._get_attr('blocks', '//channel/blocks')

    @blocks_url.setter
    def blocks_url(self, url):
        self._set_attr('blocks', '//channel/blocks', url)

    @property
    def reply_to_url(self):
        # TODO: REFACTOR
        feed = u.get_user_feed('user/feed.xml')
        return feed.xpath('channel/reply_to/link')[0].text

    @reply_to_url.setter
    def reply_to_url(self, url):
        # TODO: REFACTOR
        feed = u.get_user_feed('user/feed.xml')
        reply_to_link_element = feed.xpath('/channel/reply_to/link')
        if reply_to_link_element:
            reply_to_link_element[0].text = url
        u.write_user_feed(feed, 'user/feed.xml')

    @property
    def docs_url(self):
        return self._get_attr('docs', '//channel/docs')

    @docs_url.setter
    def docs_url(self, url):
        self._set_attr('docs', '//channel/docs', url)

    @property
    def next_node(self):
        return self._get_attr('next_node', '//channel/next_node')

    @next_node.setter
    def next_node(self, next_node):
        self._set_attr('next_node', '//channel/next_node', next_node)

    @property
    def last_build_date(self):
        return self._get_attr('last_build_date', '//channel/lastBuildDate')

    @last_build_date.setter
    def last_build_date(self, last_build_date):
        self._set_attr('last_build_date', '//channel/lastBuildDate', last_build_date)

    @property
    def relocate_url(self):
        return self._get_attr('relocate', '//channel/relocate')

    @relocate_url.setter
    def relocate_url(self, url):
        self._set_attr('relocate', '//channel/relocate', url)


    ################ Methods ##################
    # TODO: REFACTOR EVERYTHING IN User BELOW THIS POINT
    # Posting

    def add_post(self, new_post):
        """ Adds the given post to the user's feed. """
        tree = u.get_user_feed('user/feed.xml')
        channel = tree.xpath('//channel')[0]
        channel.append(to_element(new_post))
        _write_to_feed(tree, 'user/feed.xml')

    def delete_post(self, status_id):
        """ Deletes the post with the given id from the feed.  """
        # TODO: Test
        to_delete_qry = '/channel/items/item[@guid={0}'.format(status_id)

        feed_url, guid = _search_recurs('user/feed.xml', to_delete_qry)

        tree = u.get_user_feed(feed_url)
        item = tree.xpath('//item[@guid=$guid]', guid)
        item.getparent().remove(bad)

        u.write_user_feed(tree, 'user/feed.xml')

    # Following

    def follow(user_id, user_link, user_name):
        """ Adds a given user to the list of users to follow. """
        feed = u.get_user_feed('user/follows.xml')
        tree = feed.xpath('//channel')[0]
        element = E.item(
                E.user_id(user_id),
                E.user_name(user_name),
                E.user_link(user_link)
                )
        tree.append(element)
        _write_to_feed(feed, 'user/follows.xml')

    def unfollow(user_id, user_link, user_name):
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

    # Blocking

    def block(user_id, user_link, user_name):
        """ Adds a given user to the block list.  """
        feed = u.get_user_feed('user/blocks.xml')
        tree = feed.xpath('//channel')[0]
        element = E.item(
                E.user_id(user_id),
                E.user_name(user_name),
                E.user_link(user_link)
                )
        tree.append(element)
        _write_to_feed(feed, 'user/blocks.xml')

    def unblock(user_id, user_link, user_name):
        """ Deletes a user from the user's follow list. All 3 parameters
        are needed since the user_id and user_name may not be unique. """
        # TODO: Test
        to_delete_qry = '/channel/items/item[@user_name={0} and @user_id={1} \
                and @user_link={2}]'.format(user_name, user_id, user_link)

        feed_url, guid = _search_recurs('user/blocks.xml', to_delete_qry)

        tree = u.get_user_feed(feed_url)
        item = tree.xpath('//item[@guid=$guid]', guid)
        item.getparent().remove(bad)

        u.write_user_feed(tree, 'user/blocks.xml')

    # Timeline Methods
    # TODO: REFACTOR ALL OF THESE

    def fetch(start, n=0):
        """ Starting at the starting post id, fetches n posts (assuming the posts are ordered).
        Positive n for posts since start, negative n for previous posts.
        Zero (or nothing) for only the post with the given id. """
        # Get the tree, exract the starting point.
        tree = u.get_user_feed('user/feed.xml')
        stati = [post.post(status) for status in tree.xpath('//channel/item')]
        stati.sort(key=lambda x: parse(x['pubdate']), reverse=True)

        starting = stati.index([status for status in stati if status['guid'] == start][0])

        # Get only the single post.
        if n == 0:
            return starting

        # Get n posts.
        if n < 0:
            stati = reversed(stati)

        end = starting + abs(n)
        return stati[starting:ending]


    def fetch_top(n=25):
        """ Fetches the n most recent posts in reverse chronological order.  """
        if n < 0:
            raise IndexError

        tree = u.get_user_feed('user/feed.xml')
        stati = [post.post(status) for status in tree.xpath('//item')]
        stati.sort(key=lambda x: parse(x['pubdate']), reverse=True)
        return stati[:n]

