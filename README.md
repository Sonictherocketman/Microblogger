# Microblogger

A basic microblogging service implementing the [Open Microblog][1] standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.

[1]: https://github.com/Sonictherocketman/Open-Microblog

The service is designed to be a 'self-hosted' solution. It has 3 parts: the crawler, the feed managers, and the web-api server.

## Notes

The crawling system should not only be able to request, process, and store feeds quickly, but it should also be able to process as many feeds as possible at once. Its only job is to do those three steps (request, process, store in cache) as quickly as possible. The crawler should not be bothered with business logic or user facing features.

The updater's job is to accept requests to update a user's feed and write to the feed. It should also handle the pagination process once a user's feed surpasses the standard size/length, and creating new feeds for new users. It should not be concerned with business logic.

As for the web-api server, it should not comprise any HTML pages, instead it should be the front end for the JSON based REST APIs. Its many duties include, fulfilling requests for new posts to a given user, handling message passing (for replies/mentions), delegating tasks to the crawler and updater for on-demand crawling/updating when the desired data is not in the cache (if provided).

More information on the various parts below.

Pull requests gladly accepted.

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">Microblogger</span> by <span xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName">Brian Schrader</span> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.<br />Based on a work at <a xmlns:dct="http://purl.org/dc/terms/" href="https://github.com/Sonictherocketman/Microblogger" rel="dct:source">https://github.com/Sonictherocketman/Microblogger</a>.
