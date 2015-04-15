""" Tests for the User Module. """

import unittest
import sys

sys.path.insert(0, '../')
from feed.user import User
from feed.user import DataLocations as dl

class UserTest(unittest.TestCase):
    """ A suite of tests for the User class.

    All tests in this module are performed against
    all types of users (local, cached, remote).

    @author Brian Schrader
    @since 2015-04-14
    """

    # Some internals testing to make sure everything
    # starts out ok.

    def test_cached_user_init(self):
        some_dict = { 'some_key': 'some_value' }
        self.assertEqual(User(entries=some_dict)._status, dl.CACHED)

    def test_local_user_init(self):
        self.assertEqual(User(local_url='user/feed.xml')._status, dl.LOCAL)

    def test_generate_new_user_feed(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass


    ################### Properties #######################

    # Username

    def test_local_username(self):
        username = 'john.cleese'
        user = User(local_url='user/feed.xml')
        try:
            user.username = username
        except Exception, e:
            print e
            self.fail('Setting local user username failed.')
        self.assertEqual(user.username, username)

    def test_remote_username(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_username(self):
        username = 'graham.chapman'
        user = User(entries={ 'username': username })
        username = 'terry.gilliam'
        try:
            user.username = username
        except Exception, e:
            print e
            self.fail('Setting cached user username failed.')
        self.assertEqual(user.username, username)

    # Description

    def test_local_description(self):
        description = 'just some guy or gal... lol #NoFilter'
        user = User(local_url='user/feed.xml')
        try:
            user.description = description
        except Exception, e:
            print e
            self.fail('Setting local user description failed.')
        self.assertEqual(user.description, description)

    def test_remote_description(self):
        # TODO: Unimplemented
        self.fail('Unimplimented')
        pass

    def test_cached_description(self):
        description = 'test 1, 2, 3. Is this thing on?'
        user = User(entries={ 'description': description })
        description = 'some new description'
        try:
            user.description = description
        except Exception, e:
            print e
            self.fail('Setting cached user description failed.')
        self.assertEqual(user.description, description)

    # User_id

    def test_local_user_id(self):
        user_id = '039567839084335446434534'
        user = User(local_url='user/feed.xml')
        try:
            user.user_id = user_id
        except Exception, e:
            print e
            self.fail('Setting locl user user_id failed.')
        self.assertEqual(user.user_id, user_id)

    def test_remote_user_id(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_user_id(self):
        user_id = '544533534534543534'
        user = User(entries={ 'user_id': user_id })
        user_id = '54395490gejgo34'
        try:
            user.user_id = user_id
        except Exception, e:
            print e
            self.fail('Setting cached user_id failed.')
        self.assertEqual(user.user_id, user_id)

    # Full Name

    def test_local_full_name(self):
        full_name = 'John Jacob Jinglehiemer-Schmidt'
        user = User(local_url='user/feed.xml')
        try:
            user.full_name = full_name
        except Exception, e:
            print e
            self.fail('Setting locl user full_name failed.')
        self.assertEqual(user.full_name, full_name)

    def test_remote_full_name(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_full_name(self):
        full_name = 'Joe Blow'
        user = User(entries={ 'full_name': full_name })
        full_name = 'Joseph Blow'
        try:
            user.full_name = full_name
        except Exception, e:
            print e
            self.fail('Setting cached full_name failed.')
        self.assertEqual(user.full_name, full_name)

    # Link

    def test_local_link(self):
        link = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.link = link
        except Exception, e:
            print e
            self.fail('Setting local user link failed.')
        self.assertEqual(user.link, link)

    def test_remote_link(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_link(self):
        link = 'http://example.com'
        user = User(entries={ 'link': link })
        link = 'http://example.net'
        try:
            user.link = link
        except Exception, e:
            print e
            self.fail('Setting cached link failed.')
        self.assertEqual(user.link, link)

    # Language

    def test_local_language(self):
        language = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.language = language
        except Exception, e:
            print e
            self.fail('Setting local user language failed.')
        self.assertEqual(user.language, language)

    def test_remote_language(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_language(self):
        language = 'http://example.com'
        user = User(entries={ 'language': language })
        language = 'http://example.net'
        try:
            user.language = language
        except Exception, e:
            print e
            self.fail('Setting cached language failed.')
        self.assertEqual(user.language, language)

    # Follows

    def test_local_follows(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_remote_follows(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_follows(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    # Follows Just Links

    def test_local_follows_just_links(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_remote_follows_just_links(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_follows_just_links(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    # Follows URL

    def test_local_follows_url(self):
        follows_url = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.follows_url = follows_url
        except Exception, e:
            print e
            self.fail('Setting local user follows_url failed.')
        self.assertEqual(user.follows_url, follows_url)

    def test_remote_follows_url(self):
        # TODO: Unimplemented
        self.fail('Unimplemented')
        pass

    def test_cached_follows_url(self):
        follows_url = 'http://example.com'
        user = User(entries={ 'follows_url': follows_url })
        follows_url = 'http://example.net'
        try:
            user.follows_url = follows_url
        except Exception, e:
            print e
            self.fail('Setting cached follows_url failed.')
        self.assertEqual(user.follows_url, follows_url)















suite = unittest.TestLoader().loadTestsFromTestCase(UserTest)
unittest.TextTestRunner(verbosity=2).run(suite)







