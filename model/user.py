""" Feed related operations. """

import time

from lxml.builder import E
from lxml.etree import CDATA
from lxml import etree
from dateutil.parser import parse

import util as u
from settingsmanager import SettingsManager
from status import StatusType, Status, _recursive_dict

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


def _del_from_feed(rel_location, xpath):
    """ Deletes a node found at the given xpath from the feed. """
    feed = u.get_user_feed(rel_location)
    element = feed.xpath(xpath)
    if element:
        element[0].getparent().remove(element[0])
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
    feed = u.get_user_feed(rel_location)
    item = feed.xpath(xpath_qry)
    next_node = feed.xpath('//next_node')

    print xpath_qry
    print item

    if len(item) > 0:
        return rel_location, item[0].get('guid')
    elif next_node:
        # TODO: DOES NOT WORK
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
                        break



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
        elif isinstance(local_url, str) or isinstance(local_url, unicode):
            """ Create new local User with feed @ location. """
            self._status = DataLocations.LOCAL
            self._rel_location = local_url
            if force_cache: self._cache_user()
        elif isinstance(remote_url, str) or isinstance(remote_url, unicode):
            """ Create new remote user with feed @ location. """
            self._status = DataLocations.REMOTE
            self._feed_url = remote_url
            if force_cache: self._cache_user()
        else:
            raise UserNotBackedError('No backing store was provided for user.')

    @staticmethod
    def create(username):
        """ Creates a new user backing store.
        A user_id is automatically assigned, and related files are linked.
        @returns new_user, feed_location, blocks_location, follows_location
        """
        from uuid import uuid4
        user_id = str(uuid4())
        user_dir = 'user/{}'.format(user_id)

        # Create a folder to host the user's files.
        import os
        os.mkdir(user_dir)
        feed_location = '{}/feed.xml'.format(user_dir)
        blocks_location = '{}/blocks.xml'.format(user_dir)
        follows_location = '{}/follows.xml'.format(user_dir)

        User._generate_new_user_feed(feed_location)
        User._generate_new_block_list(blocks_location)
        User._generate_new_follows_list(follows_location)

        user = User(local_url=feed_location)
        user.user_id = user_id
        user.username = username

        return user, feed_location, blocks_location, follows_location

    @staticmethod
    def _generate_new_user_feed(location):
        """ Creates a blank XML feed and writes it. To fill in the
        information for the feed use the other helper methods provided. """
        feed = E.channel(
                E.username(''),
                E.user_id(''),
                E.user_full_name(''),
                E.description(CDATA('')),
                E.link(''),
                E.blocks('', count='0'),
                E.follows('', count='0'),
                E.docs(''),
                E.language(''),
                E.lastBuildDate(''),
                E.message('')
                )
        tree = etree.ElementTree(element=feed)
        u.write_user_feed(tree, location)

    @staticmethod
    def _generate_new_block_list(location):
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
        tree = etree.ElementTree(element=feed)
        u.write_user_feed(tree, location)

    @staticmethod
    def _generate_new_follows_list(location):
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
        tree = etree.ElementTree(element=feed)
        u.write_user_feed(tree, location)

    ############# Behind the Curtain ################

    def _get_attr(self, attr, xpath):
        """ Fetches the given attr based on the user's status.

        If a user is remote, then the user will first be fully
        cached before a result is returned. From that point on
        the user's cached values will be used (unless cleared).
        """
        if self._status == DataLocations.LOCAL:
            return self._get_attr_el(self._rel_location, attr, xpath)[0].text
        elif self._status == DataLocations.REMOTE:
            self.cache_user()
        return self.__dict__.get(attr)

    def _set_attr(self, attr, xpath, value):
        """ Sets the given attr to the value. If the user is NOT a
        local user, then that user's cached values are updated.
        """
        if self._status == DataLocations.LOCAL:
            _set_to_feed(self._rel_location, xpath, value)
        elif self._status == DataLocations.REMOTE:
            raise RemoteUserPropertyError
        else:
            self.__dict__[attr] = value

    def _get_attr_el(self, location, attr, xpath):
        """ A more generic form of _get_attr that returns a
        list of all elements matching the given xpath.
        """
        if self._status != DataLocations.LOCAL:
            raise UserNotBackedError(\
                    'To get the elements of a feed, the user must be local.')
        return u.get_user_feed(location).xpath(xpath)


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

    # Profile

    def get_profile(self):
        return self._get_attr(self.get_profile.binding,
                '//channel/profile')
    get_profile.binding = 'profile'

    def set_profile(self, profile):
        self._set_attr(self.set_profile.binding,
                '//channel/profile', profile)
    set_profile.binding = 'profile'

    profile = property(get_profile, set_profile)

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

    def get_follows(self):
        """ Get the list of the people the user follows. """
        follows = []
        if self._status == DataLocations.CACHED:
            follows = self.__dict__.get('follows')
        else:
            # Get the users from the feed.
            # TODO: Only works for local users.
            items = []
            if self._status == DataLocations.LOCAL:
                location = SettingsManager.get_user(self.user_id)['follows_location']
                item_els = self._get_attr_el(location, self.get_follows.binding, '//channel/item')
                follows = [_recursive_dict(item)[1] for item in item_els]

            follows = [User(remote_url=item['user_link']) for item in follows]
            cache_users(follows)
        return follows
    get_follows.binding = 'follows_items'

    follows = property(get_follows)

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
        blocks = []
        if self._status == DataLocations.LOCAL:
            location = SettingsManager.get_user()['blocks_location']
            feed = u.get_user_feed('user/blocks.xml')
            blocks_el = feed.xpath('//channel/item')
            for user_el in blocks_el:
                user_dict = _recursive_dict(user_el)[1]
                blocks.append(User(**user_dict))
        elif self._status == DataLocations.REMOTE:
            crawler = OnDemandCrawler()
            items = crawler.get_all_items(self.blocks_url)
            for item in items:
                blocks.append(User(entries=item))
        else:
            blocks = self.__dict__.get('blocks')
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

    # Message

    def get_message_url(self):
        return self._get_attr(self.get_docs_url.binding,
                '//channel/message')
    get_message_url.binding = 'message'

    def set_message_url(self, url):
        self._set_attr(self.set_mesage_url.binding,
                '//channel/message', url)
    set_message_url.binding = 'message'

    messageurl = property(get_message_url, set_message_url)

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
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot add posts to non-local user.')
        tree = u.get_user_feed(self._rel_location)
        channel = tree.xpath('//channel')[0]
        channel.append(new_post.to_element())
        _write_to_feed(tree, self._rel_location)

    def delete_post(self, status_id):
        """ Deletes the post with the given id from the feed.  """
        # TODO: Test
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot delete posts from non-local user.')
        to_delete_qry = '/channel/items/item[@guid={0}'.format(status_id)

        feed_url, guid = _search_recurs(self._rel_location, to_delete_qry)

        tree = u.get_user_feed(feed_url)
        item = tree.xpath('//item[@guid=$guid]', guid)
        item.getparent().remove(bad)

        u.write_user_feed(tree, self._rel_location)

    # Following

    def follow(self, user_id=None, user_link=None, user_name=None):
        """ Adds a given user to the list of users to follow.
        If only a user_link is provided, then the rest of the
        information will be collected from the feed.
        """
        user = None
        if user_link is not None and (user_id is None or user_name is None):
            # Go get the user's details.
            user = User(remote_url=user_link)
        if user.link is None or user.username is None or user.user_id is None:
            # Assert that all data is collected.
            user = None

        if user is None:
            raise UserNotBackedError('Cannot follow a non-backed user.')
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot add follows to non-local user.')
        location = SettingsManager.get_user(self.user_id)['follows_location']
        feed = u.get_user_feed(location)
        tree = feed.xpath('//channel')[0]
        element = E.item(
                E.user_id(user.user_id),
                E.user_name(user.username),
                E.user_link(user.link)
                )
        tree.append(element)
        _write_to_feed(feed, location)

    def unfollow(self, user_id, user_link, user_name):
        """ Deletes a user from the user's follow list. All 3 parameters
        are needed since the user_id and user_name may not be unique. """
        # TODO: Test
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot add follows to non-local user.')
        to_delete_qry = '/channel/item[user_name=\'{0}\' and user_id=\'{1}\']'\
                .format(user_name, user_id)
        location = SettingsManager.get_user(self.user_id)['follows_location']
        feed_url, guid = _search_recurs(location, to_delete_qry)
        _del_from_feed(feed_url, to_delete_qry)

    # Blocking

    def block(self, user_id, user_link, user_name):
        """ Adds a given user to the block list.  """
        user = None
        if user_link is not None and (user_id is None or user_name is None):
            # Go get the user's details.
            user = User(remote_url=user_link)
        if user.link is None or user.username is None or user.user_id is None:
            # Assert that all data is collected.
            user = None

        if user is None:
            raise UserNotBackedError('Cannot follow a non-backed user.')
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot add follows to non-local user.')
        location = SettingsManager.get_user(self.user_id)['blocks_location']
        feed = u.get_user_feed(location)
        tree = feed.xpath('//channel')[0]
        element = E.item(
                E.user_id(user.user_id),
                E.user_name(user.username),
                E.user_link(user.link)
                )
        tree.append(element)
        _write_to_feed(feed, 'user/blocks.xml')

    def unblock(self, user_id, user_link, user_name):
        """ Deletes a user from the user's follow list. All 3 parameters
        are needed since the user_id and user_name may not be unique. """
        # TODO: Test
        if self._status != DataLocations.LOCAL:
            raise RemoteUserPropertyError('Cannot add blocks to non-local user.')
        location = SettingsManager.get_user(self.user_id)['blocks_location']
        to_delete_qry = '/channel/items/item[@user_name={0} and @user_id={1} \
                and @user_link={2}]'.format(user_name, user_id, user_link)

        feed_url, guid = _search_recurs(location, to_delete_qry)
        _del_from_feed(feed_url, to_delete_qry)


    # Timeline Methods

    def user_timeline(self, start=None, n=25):
        """ Fetch the user's timeline.

        Starting at the starting post id, fetches n posts (assuming the posts are ordered).
        Positive n for posts since start, negative n for previous posts.
        Zero (or nothing) for only the post with the given id. """
        # TODO: Optimize this.
        stati = []
        if self._status == DataLocations.LOCAL:
            location = SettingsManager.get_user(self.user_id)['feed_location']
            tree = u.get_user_feed(location)
            status_elements = tree.xpath('//channel/item')
            status_dicts = [_recursive_dict(status_el)[1] for status_el in
                   status_elements]
            stati = [Status(status_dict, user=self) for status_dict in status_dicts]
        elif self._status == DataLocations.REMOTE:
            from crawler.crawler import OnDemandCrawler
            crawler = OnDemandCrawler()
            items = crawler.get_all_items([self._feed_url])[self._feed_url]
            stati = [Status(item_dict) for item_dict in items]
        else:
            # TODO: Figure out cached users.
            pass

        stati.sort(key=lambda x: x.pubdate, reverse=True)
        starting = None
        if start is not None:
            starting = stati.index([status for status in stati if status.guid == start][0])
            # Get only the single post.
            if n == 0:
                return starting
            # Get n posts.
            if n < 0:
                stati = reversed(stati)
            end = starting + abs(n)
            return stati[starting:ending]
        elif n == 0:
            return stati[0]
        else:
            return stati[:n]

    def home_timeline(self, start=None, n=25):
        """ Fetches the user's home timeline.

        This is a collection of posts from the people the user follows.
        They are ordered reverse chronologically.
        """
        # TODO: Optimize this.
        follow_urls = self.follows_just_links
        follow_urls.append(self.link)
        from crawler.crawler import OnDemandCrawler
        crawler = OnDemandCrawler()
        items_by_link = crawler.get_all_items(follow_urls)
        all_items = []
        for link, items in items_by_link.iteritems():
            all_items += items
        timeline = []
        for status_dict in all_items:
            user = User(entries=status_dict['user'])
            timeline.append(Status(status_dict, user=user))
        timeline.sort(key=lambda x: x.pubdate, reverse=True)
        return timeline[:n]

