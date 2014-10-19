Microblogger
=============

The first microblogging service implementing the [Open Microblog][1] standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.

[1]: https://github.com/Sonictherocketman/Open-Microblog

The Microblogger service is designed to have 4 parts: the crawler, the updater, the web-api server, and the caching database. The crawlers being the most important part since they need to be able to operate at close to real time.

The crawling system should not only be able to request, process, and store feeds quickly, but it should also be able to process as many feeds as possible at once. Its only job is to do those three steps (request, process, store) as quickly as possible. The crawler should not be bothered with business logic or user facing features.

The updater's job is mearly to accept requests to update a user's feed and write to the feed. It should also handle the pagination process once a user's feed surpasses the standard size/length. It should not be concerned with business logic.

As for the web-api server, it should not comprise any HTML pages, instead it should be the front end for the caching database and contain the business logic for the service. Its many duties include, fulfilling requests for new posts to a given user, handling message passing (for replies/mentions),  

The code for the service is laid out as follows.

` microblogger/
`     crawler/
`     web-api/
`
`
`
