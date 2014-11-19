# Microblogger

A basic microblogging service implementing the [Open Microblog][1] standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.

[1]: https://github.com/Sonictherocketman/Open-Microblog

The service is designed to be a 'self-hosted' solution. It has 3 parts: the crawler, the feed managers, and the web-api server.

## Notes

The crawling system should not only be able to request, process, and store feeds quickly, but it should also be able to process as many feeds as possible at once. Its only job is to do those three steps (request, process, store in cache) as quickly as possible. The crawler should not be bothered with business logic or user facing features.

The updater's job is to accept requests to update a user's feed and write to the feed. It should also handle the pagination process once a user's feed surpasses the standard size/length, and creating new feeds for new users. It should not be concerned with business logic.

As for the web-api server, it should not comprise any HTML pages, instead it should be the front end for the JSON based REST APIs. Its many duties include, fulfilling requests for new posts to a given user, handling message passing (for replies/mentions), delegating tasks to the crawler and updater for on-demand crawling/updating when the desired data is not in the cache (if provided). The web-api server will be run on [Flask][2].

[2]: http://flask.pocoo.org/ 

Pull requests gladly accepted.
