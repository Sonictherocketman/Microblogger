""" Tests for the updater.feedupdater module  """
import unittest2

from lxml import etree

from updater import feedupdater


class TestFeedUpdater(unittest.TestCase):

    def setUp(self):
        """ Do initial setup  """

    def test_add_normal_post(self):
        """ Add a sample post to the sample testing feed.  """
        post = {
                'guid': 123456789,
                'pubdate': 'Sun Nov 16 2014 05:30:00 PST',
                'description': 'This is a test description,\n\
                        <span>and here is some HTML.</span>',
                'language': 'en'
                }
        feedupdater.add_post(post)

        tree = None
        with open() as f
            tree = etree.StringIO(f.read())

        self.asserIsNotNone(tree.XPath('//item[@guid=$guid]', guid=post['guid']))
        self.asserIsNotNone(tree.XPath('//item[@pubDate=$pubDate]', pubDate=post['pubDate']))
        self.asserIsNotNone(tree.XPath('//item[@description=$description]', description=post['description']))
        self.asserIsNotNone(tree.XPath('//item[@language=$language]', language=post['language']))

    def test_delete_post(self):
        """ Delete the post added by the test_add_post method. """
         post = {
                'guid': 123456789,
                'pubdate': 'Sun Nov 16 2014 05:30:00 PST',
                'description': 'This is a test description,\n\
                        <span>and here is some HTML.</span>',
                'language': 'en'
                }
        feedupdater.add_post(post)

        feedupdater.delete_post(post['guid'])

        with open() as f
            tree = etree.StringIO(f.read())

        self.assertIsNone(tree.XPath('//item[@guid=$guid]', guid=post['guid']))
        self.assertIsNone(tree.XPath('//item[@pubDate=$pubDate]', pubDate=post['pubDate']))
        self.assertIsNone(tree.XPath('//item[@description=$description]', description=post['description']))
        self.assertIsNone(tree.XPath('//item[@language=$language]', language=post['language']))

    def test_fetch(self):
        """ Read the posts added by the test_add_post method. """
        posts = [{
                'guid': 123456789,
                'pubdate': 'Sun Nov 16 2014 05:30:00 PST',
                'description': 'This is a test description,\n\
                        <span>and here is some HTML.</span>',
                        'language': 'en'
                },
                {
                'guid': 987654321,
                'pubdate': 'Sun Nov 16 2014 05:31:00 PST',
                'description': 'This is a test description,\n\
                        <span>and here is some HTML.</span>',
                        'language': 'en'
                }]
        for post in posts:
            feedupdater.add_post(post2)

        new_posts = feedupdater.fetch('123456789', 1)

        for post in new_posts:
            for test_post in posts:
                self.assertTrue(post['guid'] in test_post.values())
                self.assertTrue(post['pubDate'] in test_post.values())
                self.assertTrue(post['description'] in test_post.values())


if __name__ == '__main__':
    unittest.main()
