""" A FeedCrawler subclass """

from microblogcrawler.crawler import FeedCrawler
from util import to_cache, add_post_to_cache
from feedreader import get_user_follows, get_user_blocks

class MicroblogFeedCrawler(FeedCrawler):
    """ A subclass of the microblogcrawler. """

    def __init__(self):
        """ Init a new crawler. """
        # If a user is blocking a given user, then do
        # not show their messages or replies.
        self.block_list = []
        self.ignore_user = False

        super(MicroblogFeedCrawler, self).__init__()

    def on_start(self):
        """ Refresh the follows list and the blocks list. """
        self.block_list = get_user_blocks()
        return get_user_follows()

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

