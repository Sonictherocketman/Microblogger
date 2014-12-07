""" A FeedCrawler subclass """

from microblogcrawler.crawler import FeedCrawler
from util import to_cache, add_post_to_cache
from feed.feedreader import get_user_follows_links, get_user_blocks_links

class MicroblogFeedCrawler(FeedCrawler):
    """ A subclass of the microblogcrawler. """

    def __init__(self, links, start_now=False, deep_traverse=False):
        """ Init a new crawler. """
        # If a user is blocking a given user, then do
        # not show their messages or replies.
        self.block_list = []
        self.ignore_user = False

        FeedCrawler.__init__(self, links, start_now=start_now, deep_traverse=deep_traverse)

    def on_start(self):
        """ Refresh the follows list and the blocks list. """
        self.block_list = get_user_blocks_links()
        return get_user_follows_links()

    def on_finish(self):
        """ Handle end of crawling process. """
        # TODO
        pass

    def on_info(self, info):
        """ Handle the new info for a feed. """
        # TODO
        pass

    def on_item(self, item):
        """ Store new items in the cache. """
        # TODO
        pass

