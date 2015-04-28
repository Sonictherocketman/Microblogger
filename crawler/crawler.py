""" A FeedCrawler subclass """

from microblogcrawler.crawler import FeedCrawler
from util import from_settings
from feed.feedreader import get_user_link, get_user_follows_links, get_user_blocks_links
from post import post
from cachemanager import CacheManager

import time
from dateutil.parser import parse


class MicroblogFeedCrawler(FeedCrawler):
    """ A basic subclass of the microblogcrawler. """

    def __init__(self, links, start_now=False, deep_traverse=False, cache_location=None):
        """ Init a new crawler. """
        # If a user is blocking a given user, then do
        # not show their messages or replies.
        self.block_list = []
        self.ignore_user = False
        self.user_info = []
        # Instantiate the cache manager at the location given. Now we can use the cache.
        if cache_location is None:
            raise ValueError('Cache location is required for multiprocessed crawling.')
        CacheManager(cache_location)
        # Call the superclass init.
        FeedCrawler.__init__(self, links, start_now=start_now, deep_traverse=deep_traverse)

    def on_item(self, link, info, item):
        """ Store new items in the cache. """
        item['user'] = info
        CacheManager.add_to_timeline(item)
        print item['description'] + '\n'


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
        for link in links:
            self._data[link] = []
        self.start(links)
        return self._data

    def get_user_info(self, links, deep_traverse=False):
        """ Returns a list of all of the profiles of the given users. """
        self._deep_traverse = deep_traverse
        for link in links:
            self._data[link] = []
        self.start(links)
        return [self._data[link][0]['user'] for link in links]

    def on_finish(self):
        """ Stops the crawler. """
        self.stop(now=True)


    def on_error(self, link, error):
        pass

    def on_item(self, link, info, new_item):
        """ Add the item field to the link's dict. """
        new_item['user'] = info
        items = self._data[link]
        # Reverse sort by time.
        index = [self._data[link].index(item) for item in items \
                if parse(item['pubdate']) < parse(new_item['pubdate'])]
        if len(index) == 0:
            self._data[link].insert(0, new_item)
        else:
            self._data[link].insert(index[0], new_item)
        # Only keep the last 1000
        if len(self._data[link]) > 1000:
            self._data[link]= self._data[link][0:999]


