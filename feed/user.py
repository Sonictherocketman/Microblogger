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


def cache_users(users):
    """ Converts the list of REMOTE users into CACHED
    users more efficently than calling user.cache_user() on
    each one individually.
    """
    # Fetch the data from the user's feed.
    import inspect
    from crawler.crawler import OnDemandCrawler
    remote_links = [user._feed_url for user in users]
    crawler = OnDemandCrawler()
    user_dicts = crawler.get_user_info(remote_links)
    # Set the data from the feed to the user's properties.
    for user in users:
        for i, user_dict in enumerate(user_dicts):
            user_methods = inspect.getmembers(User, predicate=inspect.ismethod)
            user._status = DataLocations.CACHED
            for key, value in user_dict.iteritems():
                for name, method in user_methods:
                    is_setter = name[0:3] == 'set'
                    is_bound_to_key = False
                    try:
                        is_bound_to_key = method.binding == key
                    except AttributeError as e:
                        pass
                    if is_setter and is_bound_to_key:
                        method(user, value)

    # Local Users
    #if len(local_users) > 0:
    #    user_methods = inspect.getmembers(user, predicate=inspect.ismethod)
    #    user_dict = { prop: getattr(self, prop) for prop in property_bindings }
    #
    #    for user in local_users:
    #        user._status = DataLocations.CACHED
    #        [setattr(user, key, value) for key, value in user_dict]


class NoSuchUserError(Exception):
    """ Signifies that the desired user does not exist. """
    pass


class RemoteUserPropertyError(Exception):
    """ Occurs when trying to set the properties of a REMOTE user. """
    pass


class UserNotBackedError(Exception):
    """ Signifies that a temp user is being purged and the user has
    no backing feed. """
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

    def __init__(self, local_url=None, remote_url=None, entries=None, force_cache=False):
        if isinstance(entries, dict):
            """ Create new User from dict. """
            self._status = DataLocations.CACHED
            self.__dict__.update(**entries)
        elif isinstance(local_url, str):
            """ Create new local User with feed @ location. """
            self._status = DataLocations.LOCAL
            self._rel_location = local_url
            if force_cache: self._cache_user()
        elif isinstance(remote_url, str):
            """ Create new remote user with feed @ location. """
            self._status = DataLocations.REMOTE
            self._feed_url = remote_url
            if force_cache: self._cache_user()

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

    ############# Behind the Curtain ################

    def _get_attr(self, attr, xpath):
        """ Fetches the given attr based on the user's status.

        If a user is remote, then the user will first be fully
        cached before a result is returned. From that point on
        the user's cached values will be used (unless cleared).
        """
        if self._status == DataLocations.LOCAL:
            return _get_from_feed(self._rel_location, xpath)
        elif self._status == DataLocations.REMOTE:
            self.cache_user()
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

    ################# Caching ###################

    def cache_user(self):
        """ Given a remote, or local user, converts them into a cached user.

        To convert multiple users at once use {@code cache_users()}
        @see cache_users
        """
        cache_users([self])

    def invalidate_cached_user(self):
        """ Drops the user's cached data and sets the user back to either REMOTE
        or LOCAL depending on the initial configuration. If the user is only cached
        then raises UserNotBackedError.
        """
        if self._status == DataLocations.CACHED:
            if getattr(self, '_rel_location', None) is not None:
                # TODO Dump props
                self._status = DataLocations.LOCAL
            elif getattr(self, '_feed_url', None) is not None:
                # TODO Dump props
                self._status = DataLocations.REMOTE
            else:
                raise UserNotBackedError

    ############# Properties ##############

    # Username

    def get_username(self):
        return self._get_attr(self.get_username.binding,
                '//channel/username')
    get_username.binding = 'username'

    def set_username(self, username):
        self._set_attr(self.set_username.binding,
                '//channel/username', username)
    set_username.binding = 'username'

    username = property(get_username, set_username)

    # Description

    def get_description(self):
        return self._get_attr(self.get_description.binding,
                '//channel/description')
    get_description.binding = 'description'

    def set_description(self, description):
        self._set_attr(self.set_description.binding,
                '//channel/description', description)
    set_description.binding = 'description'

    description = property(get_description, set_description)

    # User_id

    def get_user_id(self):
        return self._get_attr(self.get_user_id.binding,
                '//channel/user_id')
    get_user_id.binding = 'user_id'

    def set_user_id(self, user_id):
        self._set_attr(self.get_user_id.binding,
                '//channel/user_id', user_id)
    set_user_id.binding = 'user_id'

    user_id = property(get_user_id, set_user_id)

    # Full Name

    def get_full_name(self):
        return self._get_attr(self.get_full_name.binding,
                '//channel/user_full_name')
    get_full_name.binding = 'user_full_name'

    def set_full_name(self, full_name):
        self._set_attr(self.set_full_name.binding,
                '//channel/user_full_name', full_name)
    set_full_name.binding = 'user_full_name'

    full_name = property(get_full_name, set_full_name)

    # Link

    def get_link(self):
        return self._get_attr(self.get_link.binding,
                '//channel/link')
    get_link.binding = 'link'

    def set_link(self, link):
        self._set_attr(self.set_link.binding,
                '//channel/link', link)
    set_link.binding = 'link'

    link = property(get_link, set_link)

    # Language

    def get_language(self):
        return self._get_attr(self.get_language.binding,
                '//channel/language')
    get_language.binding = 'language'

    def set_language(self, language):
        self._set_attr(self.set_language.binding,
                '//channel/language', language)
    set_language.binding = 'language'

    language = property(get_language, set_language)

    # Follows

    @property
    def follows(self):
        """ Get the list of the people the user follows. """
        # TODO: FIX THIS - This only works for LOCAL users.
        feed = u.get_user_feed('user/follows.xml')
        follows = []
        follows_el = feed.xpath('//channel/item')
        if not len(follows_el) > 0:
            return list()

        for user_el in follows_el:
            user_dict = post._recursive_dict(user_el)[1]
            follows.append(User(entries=user_dict))
        return follows

    @property
    def follows_just_links(self):
        """ Gets the list of links to the feeds the user follows.
        Basically a simplified version of get_user_follows. """
        return [user.link for user in self.follows]

    # Follows Url

    def get_follows_url(self):
        return self._get_attr(self.get_follows_url.binding,
                '//channel/follows')
    get_follows_url.binding = 'follows'

    def set_follows_url(self, url):
        self._set_attr(self.set_follows_url.binding,
                '//channel/follows', url)
    set_follows_url.binding = 'follows'

    follows_url = property(get_follows_url, set_follows_url)

    # Blocks

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

    # Blocks Url

    def get_blocks_url(self):
        return self._get_attr(self.get_blocks_url.binding,
                '//channel/blocks')
    get_blocks_url.binding = 'blocks'

    def set_blocks_url(self, url):
        self._set_attr(self.set_blocks_url.binding,
                '//channel/blocks', url)
    set_blocks_url.binding = 'blocks'

    blocks_url = property(get_blocks_url, set_blocks_url)

    # Reply To

    def get_reply_to_url(self):
        # TODO: REFACTOR
        feed = u.get_user_feed('user/feed.xml')
        return feed.xpath('channel/reply_to/link')[0].text
    get_reply_to_url.binding = 'reply_to'

    def set_reply_to_url(self, url):
        # TODO: REFACTOR
        feed = u.get_user_feed('user/feed.xml')
        reply_to_link_element = feed.xpath('/channel/reply_to/link')
        if reply_to_link_element:
            reply_to_link_element[0].text = url
        u.write_user_feed(feed, 'user/feed.xml')
    set_reply_to_url.binding = 'reply_to'

    reply_to_url = property(get_reply_to_url, set_reply_to_url)

    # Docs

    def get_docs_url(self):
        return self._get_attr(self.get_docs_url.binding,
                '//channel/docs')
    get_docs_url.binding = 'docs'

    def set_docs_url(self, url):
        self._set_attr(self.get_docs_url.binding,
                '//channel/docs', url)
    set_docs_url.binding = 'docs'

    docs_url = property(get_docs_url, set_docs_url)

    # Next Node

    def get_next_node(self):
        return self._get_attr(self.get_next_node.binding,
                '//channel/next_node')
    get_next_node.binding = 'next_node'

    def set_next_node(self, next_node):
        self._set_attr(self.set_next_node.binding,
                '//channel/next_node', next_node)
    set_next_node.binding = 'next_node'

    next_node = property(get_next_node, set_next_node)

    # Last Build Date

    def get_last_build_date(self):
        return self._get_attr(get_last_build_date.binding,
                '//channel/lastBuildDate')
    get_last_build_date.binding = 'lastBuildDate'

    def set_last_build_date(self, last_build_date):
        self._set_attr(self.set_last_build_date.binding,
                '//channel/lastBuildDate', last_build_date)
    set_last_build_date.binding = 'lastBuildDate'

    last_build_date = property(get_last_build_date, set_last_build_date)

    # Relocate

    # TODO: Relocate setter should insert a new element instead of jsut setting
    # This is because the element should only exist if the relocate is filled.

    def get_relocate_url(self):
        return self._get_attr(self.get_relocate_url.binding,
                '//channel/relocate')
    get_relocate_url.binding = 'relocate'

    def set_relocate_url(self, url):
        self._set_attr(self.set_last_build_date.binding,
                '//channel/relocate', url)
    set_relocate_url.binding = 'relocate'

    relocate = property(get_relocate_url, set_relocate_url)


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

