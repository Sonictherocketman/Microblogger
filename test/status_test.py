""" A series of tests for the status module. """


import unittest
import sys

from lxml.builder import E
from lxml.etree import CDATA

sys.path.insert(0, '../')
from feed.status import Status, DATE_STR_FORMAT, StatusType




class StatusTest(unittest.TestCase):

    def test_status_init(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'Hey hey hey.'
                }
        status = Status(status_dict)
        self.assertEqual(status.status_type, StatusType.STATUS)

    def test_status_init_reply(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'in_reply_to_status_id': '23456543',
                'in_reply_to_user_id': '34534',
                'in_reply_to_user_link': 'http://example.com'
                }
        status = Status(status_dict)
        self.assertEqual(status.status_type, StatusType.REPLY)

    def test_status_init_repost(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'reposted_status_pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'reposted_status_user_id': '34534',
                'reposted_status_user_link': 'http://example.com',
                'reposted_status_id': '234543'
                }
        status = Status(status_dict)
        self.assertEqual(status.status_type, StatusType.REPOST)

    def test_is_standard_status(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'Hey hey hey.'
                }
        status = Status(status_dict)
        self.assertTrue(status.is_standard())

    def test_is_standard_reply(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'in_reply_to_status_id': '23456543',
                'in_reply_to_user_id': '34534',
                'in_reply_to_user_link': 'http://example.com'
                }
        status = Status(status_dict, StatusType.REPLY)
        self.assertTrue(status.is_standard())

    def test_is_standard_repost(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'reposted_status_pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'reposted_status_user_id': '34534',
                'reposted_status_user_link': 'http://example.com',
                'reposted_status_id': '234543'
                }
        status = Status(status_dict, StatusType.REPOST)
        self.assertTrue(status.is_standard())

    def test_to_element(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'Hey hey hey.'
                }
        status = Status(status_dict)
        el = status.to_element()

        guid = el.xpath('/item/guid/text()')[0]
        self.assertEqual(guid , status_dict['guid'])
        pubdate = el.xpath('/item/pubdate/text()')[0]
        #self.assertEqual(pubdate, status_dict['pubdate'])
        description = el.xpath('/item/description/text()')[0]
        self.assertEqual(description, status_dict['description'])

    def test_to_element_reply(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'in_reply_to_status_id': '23456543',
                'in_reply_to_user_id': '34534',
                'in_reply_to_user_link': 'http://example.com'
                }
        status = Status(status_dict, StatusType.REPLY)
        el = status.to_element()
        guid = el.xpath('/item/guid/text()')[0]
        self.assertEqual(guid , status_dict['guid'])
        pubdate = el.xpath('/item/pubdate/text()')[0]
        #self.assertEqual(pubdate, status_dict['pubdate'])
        description = el.xpath('/item/description/text()')[0]
        self.assertEqual(description, status_dict['description'])

        in_reply_to_status_id = el.xpath('/item/in_reply_to_status_id/text()')[0]
        self.assertEqual(in_reply_to_status_id, status_dict['in_reply_to_status_id'])

        in_reply_to_user_id = el.xpath('/item/in_reply_to_user_id/text()')[0]
        self.assertEqual(in_reply_to_user_id, status_dict['in_reply_to_user_id'])

        in_reply_to_user_link = el.xpath('/item/in_reply_to_user_link/text()')[0]
        self.assertEqual(in_reply_to_user_link, status_dict['in_reply_to_user_link'])

    def test_to_element_repost(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'description': 'hey hey hey.',
                'reposted_status_pubdate': 'Thu, May 7 2015 12:02:30 +0000',
                'reposted_status_user_id': '34534',
                'reposted_status_user_link': 'http://example.com',
                'reposted_status_id': '234543'
                }
        status = Status(status_dict, StatusType.REPOST)
        el = status.to_element()

        reposted_status_pubdate = el.xpath('/item/reposted_status_pubdate/text()')[0]
        #self.assertEqual(reposted_status_pubdate, status_dict['reposted_status_pubdate'])

        reposted_status_user_id = el.xpath('/item/reposted_status_user_id/text()')[0]
        self.assertEqual(reposted_status_user_id, status_dict['reposted_status_user_id'])

        reposted_status_user_link = el.xpath('/item/reposted_status_user_link/text()')[0]
        self.assertEqual(reposted_status_user_link, status_dict['reposted_status_user_link'])

        reposted_status_id = el.xpath('/item/reposted_status_id/text()')[0]
        self.assertEqual(reposted_status_id, status_dict['reposted_status_id'])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StatusTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
