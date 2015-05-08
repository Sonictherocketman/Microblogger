""" A series of tests for the status module. """


import unittest
import sys

sys.path.insert(0, '../')
from feed.status import Status, DATE_STR_FORMAT, StatusType




class StatusTest(unittest.TestCase):

    def test_status_init(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
                'description': 'Hey hey hey.'
                }
        status = Status(status_dict)
        self.assertEqual(status.status_type, StatusType.STATUS)

    def test_status_init_reply(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
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
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
                'description': 'hey hey hey.',
                'reposted_status_pubdate': '23456543',
                'reposted_status_user_id': '34534',
                'reposted_status_user_link': 'http://example.com',
                'reposted_status_id': '234543'
                }
        status = Status(status_dict)
        self.assertEqual(status.status_type, StatusType.REPOST)

    def test_is_standard_status(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
                'description': 'Hey hey hey.'
                }
        status = Status(status_dict)
        self.assertTrue(status.is_standard())

    def test_is_standard_reply(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
                'description': 'hey hey hey.',
                'in_reply_to_status_id': '23456543',
                'in_reply_to_user_id': '34534',
                'in_reply_to_user_link': 'http://example.com'
                }
        status = Status(status_dict)
        self.assertTrue(status.is_standard())

    def test_is_standard_repost(self):
        status_dict = {
                'guid': '1234567876543',
                'pubdate': 'Thu, May 7 2015 12:02:30 UTC',
                'description': 'hey hey hey.',
                'reposted_status_pubdate': '23456543',
                'reposted_status_user_id': '34534',
                'reposted_status_user_link': 'http://example.com',
                'reposted_status_id': '234543'
                }
        status = Status(status_dict)
        print status.status_type
        self.assertTrue(status.is_standard())




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StatusTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
