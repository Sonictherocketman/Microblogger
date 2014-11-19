""" Tests for the feedgenerator module.  """

from ..updater import feedgenerator as fg

import unittest
import os

from lxml import etree

class FeedGeneratorTest(unittest.TestCase):
    """   """

    def setUp():
        """ Initial setup """


    def test_generate_new_feed(self):
        """ Tests the generation of a new main user feed. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        fg.generate_new_feed('test/feed.xml')

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertIsNotNone(tree)

    def test_generate_new_block_list(self):
        """ Tests the generation of a new block list. """
        if os.path.isfile('test/blocks.xml'):
            os.remove('test/blocks.xml')

        fg.generate_new_block_list('test/blocks.xml')

        tree = None
        with open('test/blocks.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertIsNotNone(tree)

    def test_generate_new_follows_list(self):
        """ Tests the generation of the new follows list. """
         if os.path.isfile('test/follows.xml'):
            os.remove('test/follows.xml')

        fg.generate_new_block_list('test/follows.xml')

        tree = None
        with open('test/follows.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertIsNotNone(tree)

    def test_set_username(self):
        """ Tests the setting of a username to the
        user's feed. A feed must be generated first. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        username = 'this is a testing username'
        fg.generate_new_block_list('test/feed.xml')
        fg.set_username(username)

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertEqual(username, tree.XPath('//username')[0].text)

    def test_set_full_username(self):
        """ Tests the setting of a full_username to the
        user's feed. A feed must be generated first. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        full_username = 'this is a testing full_username'
        fg.generate_new_block_list('test/feed.xml')
        fg.set_full_username(full_username)

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertEqual(full_username, tree.XPath('//full_username')[0].text)

    def test_set_user_description(self):
        """ Tests the setting of a description to the
        user's feed. A feed must be generated first. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        description = 'this is a testing description'
        fg.generate_new_block_list('test/feed.xml')
        fg.set_description(description)

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertEqual(description, tree.XPath('//description')[0].text)

    def test_set_default_language(self):
        """ Tests the setting of a language to the
        user's feed. A feed must be generated first. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        language = 'this is a testing language'
        fg.generate_new_block_list('test/feed.xml')
        fg.set_default_language(language)

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertEqual(language, tree.XPath('//language')[0].text)

    def test_set_reply_to(self):
        """ Tests the setting of a reply_to to the
        user's feed. A feed must be generated first. """
        if os.path.isfile('test/feed.xml'):
            os.remove('test/feed.xml')

        reply_to = 'this is a testing reply_to'
        fg.generate_new_block_list('test/feed.xml')
        fg.set_reply_to(reply_to)

        tree = None
        with open('test/feed.xml', 'r') as f:
            data = f.read()
            tree = etree.StringIO(data)

        self.assertEqual(reply_to, tree.XPath('//reply_to')[0].text)


    # TODO: Finish tests.

