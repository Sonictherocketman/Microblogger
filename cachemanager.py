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


import os, json
from util import to_cache, from_cache
from dateutil.parser import parse


class CacheManager():

    # Class Variables
    cache_location = None
    cache_file_location = None
    cached_post_count = 0

    # Init/Destroy

    def __init__(self, cache_location=None):
        """ Default contructor. Passing cache_location will
        create a cache, if one does not already exist, at
        that location just like create_cache.

        Cache location should be a dir to store all cache files. """
        CacheManager.cache_location = None       # The dir that holds the whole cache.
        CacheManager.cache_file_location = None  # The JSON file that contains posts, etc.

        if cache_location is not None:
            CacheManager.create_cache(cache_location)

    @staticmethod
    def create_cache(location):
        """ Creates a cache at the given location. If the cache already
        exists, then it clears it. """

        # Make sure everything is in order.
        if os.path.isfile(location):
            print 'Cache location must be a directory not a file.'
            raise IOError
        if not os.path.isdir(location):
            os.mkdir(location)

        # Set the cache file location.
        CacheManager.cache_location = location
        if location[-1] != '/':
            location += '/'
        CacheManager.cache_file_location = location + 'cache.json'

        # Write the empty cache.
        cache_data = {
                'timeline': [],
                'users': []
            }
        with open(CacheManager.cache_file_location, 'w') as f:
            f.write(json.dumps(cache_data))

    @staticmethod
    def destroy_cache():
        """ Destroys the stored cache. The file will be deleted. """
        # TODO
        pass

    @staticmethod
    def clear_cache():
        """ Clears the cache. All files remain. """
        # TODO
        pass

    # Main User's Timeline Functions

    @staticmethod
    def get_timeline(start_id=None, n=0):
        """ Retrieves the main user's cached timeline.
        In reverse chronological order. """
        full_timeline = from_cache(CacheManager.cache_file_location, 'timeline')

        # By default, return the first 25 items.
        if start_id is None:
            return full_timeline[:25]

        starting_item = [item for item in full_timeline if item['guid'] == starting_id]
        index = 0
        if len(starting_item) > 0:
            index = full_timeline.index(starting_item)

        # If no n is provided return max 25 items after the given one.
        if n is None:
            end = 25
            if len(full_timeline[index:]) < 25:
                end = len(full_timeline[index:])
            return full_timeline[index:end]

        # Return n items (forward or back) from the given point.
        if n == 0:
            return [full_timeline[index]]
        elif n < 0:
            full_timeline = reversed(full_timeline)

        return full_timeline[:abs(n)]


    @staticmethod
    def add_to_timeline(new_status):
        """ Caches the given post in the user's
        timeline. The post is inserted reverse
        chronologically. """
        timeline = CacheManager.get_timeline()
        index = [timeline.index(status) for status in timeline \
                if parse(status['pubdate']) < parse(new_status['pubdate'])]
        if len(index) == 0:
            timeline.insert(0, new_status)
        else:
            timeline.insert(index[0], new_status)

        if len(timeline) > 1000:
            timeline = timeline[0:999]
        to_cache(CacheManager.cache_file_location, 'timeline', timeline)

    @staticmethod
    def remove_from_timeline(status_id):
        """ Removes the post with the given status_id
        from the user's cached timeline. """
        timeline = [status for status in CacheManager.get_timeline \
                if status['guid'] != status_id]
        to_cache(CacheManager.cache_file_location, 'timeline', timelinE)

