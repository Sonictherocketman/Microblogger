""" A FeedCrawler subclass """

from microblogcrawler.crawler import FeedCrawler
from util import from_settings
from feed.feedreader import get_user_follows_links, get_user_blocks_links
from post import post
from cachemanager import CacheManager

import time


class MicroblogFeedCrawler(FeedCrawler):
    """ A basic subclass of the microblogcrawler. """

    def __init__(self, links, start_now=False, deep_traverse=False):
        """ Init a new crawler. """
        # If a user is blocking a given user, then do
        # not show their messages or replies.
        self.block_list = []
        self.ignore_user = False
        self.user_info = []
        FeedCrawler.__init__(self, links, start_now=start_now, deep_traverse=deep_traverse)

    def on_start(self):
        """ Refresh the follows list and the blocks list. """
        time.sleep(1)

    def on_finish(self):
        """ Handle end of crawling process. """
        pass

    def on_info(self, link, info):
        """ Handle the new info for a feed. """
        pass

    def on_item(self, link, item):
        """ Store new items in the cache. """
        CacheManager.add_to_timeline(item)


class OnDemandCrawler(FeedCrawler):
    """ A crawler that returns the data for each
    feed once the entire set of links is parsed.

    The callback recieves a dict of the data.
    {
        "[a given link]": [
            {
                'info': [],
                'items': []
            }
        ]
    }"""

    def __init__(self):
        self._data = {}
        FeedCrawler.__init__(self, [], start_now=False, deep_traverse=False)

    def get_all_items(self, links, deep_traverse=False):
        """ Does the crawling and returns when the crawling is done. """
        self._deep_traverse = deep_traverse
        self.start(links)
        return self._data

    def on_finish(self):
        """ Stops the crawler. """
        self.stop()

    def on_item(self, link, item):
        """ Add the item field to the link's dict. """
        if self._data[link] is None:
            self._data[link] = {
                    'items': [],
                    'info': []
                    }
        self._data[link]['items'].append(item)

    def on_info(self, link, item):
        """ Add the info field to the link's dict. """
        if self._data[link] is None:
            self._data[link] = {
                    'items': [],
                    'info': []
                    }
            self._data[link]['info'].append(post(info))

