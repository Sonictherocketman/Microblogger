""" A FeedCrawler subclass """

from microblogcrawler.crawler import FeedCrawler


class MicroblogFeedCrawler(FeedCrawler):
    """ A subclass of the microblogcrawler. """

    def on_start(self):
        """ Handle new feeds being inserted. """
        # TODO
        pass

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

