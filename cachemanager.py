""" Manages the CRUD of the app cache.

The app cache can store a number of things:
    - the main user's timeline (the most
        recent 1000 posts)
    - users (TODO)
    - images (TODO)

For all methodss, the cache will return None,
if no results were found or if there was a
problem.
"""


import os
from util import init_cache, to_cache, from_cache


class CacheManager():

    # Init/Destroy

    def __init__(self, cache_location=None):
        """ Default contructor. Passing cache_location will
        create a cache, if one does not already exist, at
        that location just like create_cache.

        Cache location should be a dir to store all cache files. """
        self.cache_location = None       # The dir that holds the whole cache.
        self.cache_file_location = None  # The JSON file that contains posts, etc.
        self.cached_post_count = 0

        if cache_location is not None and \
                not os.path.isfile(cache_location):
            self.create_cache(cache_location)

    def create_cache(location):
        """ Creates a cache at the given location. If the cache already
        exists, then it clears it. """

        # Make sure everything is in order.
        if not os.path.isfile(location)
            print 'Cache location must be a directory not a file.'
            raise IOError
        if not os.path.isdir(location):
            os.mkdirs(location)

        # Set the cache file location.
        self.cache_location = location
        if location[-1] != '/':
            location += '/'
        self.cache_file_location = location + 'cache.json'

        # Write the empty cache.
        cache_data = {
                'timeline': [],
                'users': []
            }
        with open(self.cache_file_location, 'w') as f:
            f.write(json.dumps(cache_data))

    def destroy_cache():
        """ Destroys the stored cache. The file will be deleted. """
        # TODO
        pass

    # Main User's Timeline Functions

    def get_timeline(self):
        """ Retrieves the main user's cached timeline.
        In reverse chronological order. """
        return from_cache(self.cache_location, 'timeline')

    def add_to_timeline(self, new_status):
        """ Caches the given post in the user's
        timeline. The post is inserted reverse
        chronologically. """
        timeline = self.get_timeline()
        index = [timeline.index(status) for status in timeline \
                if status['pubdate'] < new_status['pubdate']]
        if index is not None:
            timeline.insert(index, new_status)
        if len(timeline) > 1000:
            timeline = timeline[0:999]
        to_cache(self.cache_file_location, 'timeline', timeline)

    def remove_from_timeline(self, status_id):
        """ Removes the post with the given status_id
        from the user's cached timeline. """
        timeline = [status for status in self.get_timeline \
                if status['guid'] != status_id]
        to_cache(self.cache_file_location, 'timeline', timelinE)

