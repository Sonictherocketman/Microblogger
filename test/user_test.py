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
        some_dict = {'some_key': 'some_value'}
        self.assertEqual(User(entries=some_dict)._status, dl.CACHED)

    def test_remote_user_init(self):
        some_url = 'http://somedomain.tld/feed'
        self.assertEqual(User(remote_url=some_url)._status, dl.REMOTE)

    def test_local_user_init(self):
        self.assertEqual(User(local_url='user/feed.xml')._status, dl.LOCAL)

    #def test_generate_new_user_feed(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    ################### Caching #####################

    def test_cache_user(self):
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        user.cache_user()
        self.assertEqual(user._status, dl.CACHED)
        self.assertEqual(user.username, 'sonicrocketman')

    def test_cache_users(self):
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        from feed.user import cache_users
        cache_users([user])
        self.assertEqual(user._status, dl.CACHED)
        self.assertEqual(user.username, 'sonicrocketman')

    def test_invalidate_cached_user(self):
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        user.cache_user()
        self.assertEqual(user._status, dl.CACHED)
        self.assertEqual(user.username, 'sonicrocketman')
        user.invalidate_cached_user()
        self.assertEqual(user._status, dl.REMOTE)

    ################### Properties #######################

    # Username

    def test_local_username(self):
        username = 'john.cleese'
        user = User(local_url='user/feed.xml')
        try:
            user.username = username
        except Exception as e:
            print e
            self.fail('Setting local user username failed.')
        self.assertEqual(user.username, username)

    def test_remote_username(self):
        username = 'spam'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # Should fail.
            user.username = username
            self.fail('Setting a remote user should be forbidden.')
        except:
            pass

    def test_cached_username(self):
        username = 'graham.chapman'
        user = User(entries={ 'username': username })
        username = 'terry.gilliam'
        try:
            user.username = username
        except Exception as e:
            print e
            self.fail('Setting cached user username failed.')
        self.assertEqual(user.username, username)

    # Description

    def test_local_description(self):
        description = 'just some guy or gal... lol #NoFilter'
        user = User(local_url='user/feed.xml')
        try:
            user.description = description
        except Exception as e:
            print e
            self.fail('Setting local user description failed.')
        self.assertEqual(user.description, description)

    def test_remote_description(self):
        description = 'dummy'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # Should fail.
            user.descripton = description
            self.fail('Setting a remote user should be forbidden.')
        except:
            pass

    def test_cached_description(self):
        description = 'test 1, 2, 3. Is this thing on?'
        user = User(entries={ 'description': description })
        description = 'some new description'
        try:
            user.description = description
        except Exception as e:
            print e
            self.fail('Setting cached user description failed.')
        self.assertEqual(user.description, description)

    # User_id

    def test_local_user_id(self):
        user_id = '039567839084335446434534'
        user = User(local_url='user/feed.xml')
        try:
            user.user_id = user_id
        except Exception as e:
            print e
            self.fail('Setting local user user_id failed.')
        self.assertEqual(user.user_id, user_id)

    def test_remote_user_id(self):
        user_id = 'dummy'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # Should fail.
            user.user_id = user_id
            self.fail('Setting a remote user should be forbidden.')
        except:
            pass

    def test_cached_user_id(self):
        user_id = '544533534534543534'
        user = User(entries={'user_id': user_id})
        user_id = '54395490gejgo34'
        try:
            user.user_id = user_id
        except Exception as e:
            print e
            self.fail('Setting cached user_id failed.')
        self.assertEqual(user.user_id, user_id)

    # Full Name

    def test_local_full_name(self):
        full_name = 'John Jacob Jinglehiemer-Schmidt'
        user = User(local_url='user/feed.xml')
        try:
            user.full_name = full_name
        except Exception as e:
            print e
            self.fail('Setting locl user full_name failed.')
        self.assertEqual(user.full_name, full_name)

    def test_remote_full_name(self):
        full_name = 'dummy'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # should fail.
            user.full_name = full_name
            self.fail('setting a remote user should be forbidden.')
        except:
            pass

    def test_cached_full_name(self):
        full_name = 'Joe Blow'
        user = User(entries={'full_name': full_name})
        full_name = 'Joseph Blow'
        try:
            user.full_name = full_name
        except Exception as e:
            print e
            self.fail('Setting cached full_name failed.')
        self.assertEqual(user.full_name, full_name)

    # Link

    def test_local_link(self):
        link = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.link = link
        except Exception as e:
            print e
            self.fail('Setting local user link failed.')
        self.assertEqual(user.link, link)

    def test_remote_link(self):
        link = 'dummy'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # should fail.
            user.link = link
            self.fail('setting a remote user should be forbidden.')
        except:
            pass

    def test_cached_link(self):
        link = 'http://example.com'
        user = User(entries={ 'link': link })
        link = 'http://example.net'
        try:
            user.link = link
        except Exception as e:
            print e
            self.fail('Setting cached link failed.')
        self.assertEqual(user.link, link)

    # Language

    def test_local_language(self):
        language = 'en'
        user = User(local_url='user/feed.xml')
        try:
            user.language = language
        except Exception as e:
            print e
            self.fail('Setting local user language failed.')
        self.assertEqual(user.language, language)

    def test_remote_language(self):
        language = 'en'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # should fail.
            user.language = language
            self.fail('setting a remote user should be forbidden.')
        except Exception as e:
            pass

    def test_cached_language(self):
        language = 'en'
        user = User(entries={ 'language': language })
        language = 'http://example.net'
        try:
            user.language = language
        except Exception as e:
            print e
            self.fail('Setting cached language failed.')
        self.assertEqual(user.language, language)

    # Follows

    #def test_local_follows(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_remote_follows(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_cached_follows(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    # Follows Just Links

    def test_local_follows_just_links(self):
        user = User(local_url='user/feed.xml')
        self.assertEqual(user._status, dl.LOCAL)
        self.assertTrue(len(user.follows_just_links) > 0)

    def test_remote_follows_just_links(self):
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        self.assertEqual(user._status, dl.REMOTE)
        self.assertTrue(len(user.follows_just_links) > 0)

    def test_cached_follows_just_links(self):
        user = User(entries={ 'follows': { 'user_id': 123 } })
        self.assertEqual(user._status, dl.CACHED)
        self.assertTrue(len(user.follows_just_links) > 0)

    # Follows URL

    def test_local_follows_url(self):
        follows_url = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.follows_url = follows_url
        except Exception as e:
            print e
            self.fail('Setting local user follows_url failed.')
        self.assertEqual(user.follows_url, follows_url)

    def test_remote_follows_url(self):
        follows_url = 'http://example.com'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            # should fail.
            user.follows_url = follows_url
            self.fail('setting a remote user should be forbidden.')
        except Exception as e:
            pass

    def test_cached_follows_url(self):
        follows_url = 'http://example.com'
        user = User(entries={ 'follows_url': follows_url })
        follows_url = 'http://example.net'
        try:
            user.follows_url = follows_url
        except Exception as e:
            print e
            self.fail('Setting cached follows_url failed.')
        self.assertEqual(user.follows_url, follows_url)


    # Blocks

    #def test_local_blocks(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_remote_blocks(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_cached_blocks(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    # Blocks Just Links

    #def test_local_blocks_just_links(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_remote_blocks_just_links(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    #def test_cached_blocks_just_links(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    # Blocks URL

    def test_local_blocks_url(self):
        blocks_url = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.blocks_url = blocks_url
        except Exception as e:
            print e
            self.fail('Setting local user blocks_url failed.')
        self.assertEqual(user.blocks_url, blocks_url)

    def test_remote_blocks_url(self):
        blocks_url = 'http://example.com'
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        try:
            user.blocks_url = blocks_url
            self.fail('setting a remote user should be forbidden.')
        except Exception as e:
            pass

    def test_cached_blocks_url(self):
        blocks_url = 'http://example.com'
        user = User(entries={ 'blocks_url': blocks_url })
        blocks_url = 'http://example.net'
        try:
            user.blocks_url = blocks_url
        except Exception as e:
            print e
            self.fail('Setting cached blocks_url failed.')
        self.assertEqual(user.blocks_url, blocks_url)

    # Docs

    def test_local_docs_url(self):
        docs_url = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.docs_url = docs_url
        except Exception as e:
            print e
            self.fail('Setting local user docs_url failed.')
        self.assertEqual(user.docs_url, docs_url)

    #def test_remote_docs_url(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    def test_cached_docs_url(self):
        docs_url = 'http://example.com'
        user = User(entries={ 'docs_url': docs_url })
        docs_url = 'http://example.net'
        try:
            user.docs_url = docs_url
        except Exception as e:
            print e
            self.fail('Setting cached docs_url failed.')
        self.assertEqual(user.docs_url, docs_url)

    # Relocate

    def test_local_relocate_url(self):
        relocate_url = 'http://example.com'
        user = User(local_url='user/feed.xml')
        try:
            user.relocate_url = relocate_url
        except Exception as e:
            print e
            self.fail('Setting local user relocate_url failed.')
        self.assertEqual(user.relocate_url, relocate_url)

    #def test_remote_relocate_url(self):
    #    # TODO: Unimplemented
    #    self.fail('Unimplemented')
    #    pass

    def test_cached_relocate_url(self):
        relocate_url = 'http://example.com'
        user = User(entries={ 'relocate_url': relocate_url })
        relocate_url = 'http://example.net'
        try:
            user.relocate_url = relocate_url
        except Exception as e:
            print e
            self.fail('Setting cached relocate_url failed.')
        self.assertEqual(user.relocate_url, relocate_url)


    ################# Methods ###################

    #def test_add_and_delete_post(self):
    #    self.fail('Unimplemented')

    #def test_follow_and_unfollow_user(self):
    #    self.fail('Unimplemented')

    #def test_block_and_unblock_user(self):
    #    self.fail('Unimplemented')

    ############### Timeline Stuff ################
    def test_local_user_timeline(self):
        user = User(local_url='user/feed.xml')
        timeline = user.user_timeline()
        self.assertTrue(len(timeline) > 0)

    def test_remote_user_timeline(self):
        user = User(remote_url='http://microblog.brianschrader.com/feed')
        timeline = user.user_timeline()
        self.assertTrue(len(timeline) > 0)

    #def test_cached_user_timeline(self):
    #    pass

    # There's only 1 home timeline test because
    # it doesn't matter what kind of user it is.
    def test_home_timeline(self):
        user = User(local_url='user/feed.xml')
        timeline = user.home_timeline()
        self.assertTrue(len(timeline) > 0)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(UserTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
