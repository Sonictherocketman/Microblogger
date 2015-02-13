""" Manages the crawler and creates new crawlers if none exist.  """

import os
import sys

from crawler.crawler import MicroblogFeedCrawler
from feed import feedreader as fr
from settingsmanager import SettingsManager


PID_LOCATION = '/tmp/microblog/pid'


def main():
    # Check the user's pid file to see if
    # a crawler already exists.
    if not os.path.exists(PID_LOCATION):
        with open(PID_LOCATION, 'w') as f:
            f.write('working')

        print 'Starting...'
        crawler = MicroblogFeedCrawler([],
                cache_location=SettingsManager.get('cache_location'))
        crawler.start()


if __name__ == '__main__':
    main()
