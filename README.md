# Microblogger

The first microblogging service implementing the [Open Microblog][1] standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.

[1]: https://github.com/Sonictherocketman/Open-Microblog

The Microblogger service is designed to have 4 parts: the crawler, the updater, the web-api server, and the caching database. The crawlers being the most important part since they need to be able to operate at close to real time. Each part is a Python sub-package in the overall microblog package. The idea being that anyone could pull the source, add their backing store and caching database and be have basic service either for themselves or for a business.

Although this is a predominantly Python project (the crawler and updater will be in Python) the front end is still up for debate. Python is preferred but Node.js is being considered. The caching database will use [MongoDB][2] which is not really up for debate, unless you have a really convincing argument.

[2]: http://www.mongodb.com

The crawling system should not only be able to request, process, and store feeds quickly, but it should also be able to process as many feeds as possible at once. Its only job is to do those three steps (request, process, store) as quickly as possible. The crawler should not be bothered with business logic or user facing features.

The updater's job is to accept requests to update a user's feed and write to the feed. It should also handle the pagination process once a user's feed surpasses the standard size/length, and creating new feeds for new users. It should not be concerned with business logic.

As for the web-api server, it should not comprise any HTML pages, instead it should be the front end for the JSON based REST APIs using the caching database and the business logic for the service. Its many duties include, fulfilling requests for new posts to a given user, handling message passing (for replies/mentions), delegating tasks to the crawler and updater for on-demand crawling/updating when the desired data is not in the caching database.

More information on the various parts below.

Pull requests gladly accepted.

## Notes

As for what tech stack will support the web-api server, or for that matter, what language it will use (since Python isn't required) that has not yet been decided. At time of writing, either a Django or Node.js options are being considered, though suggestions are welcome. 


<small><center><a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">Microblogger</span> by <span xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName">Brian Schrader</span> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.<br />Based on a work at <a xmlns:dct="http://purl.org/dc/terms/" href="https://github.com/Sonictherocketman/Microblogger" rel="dct:source">https://github.com/Sonictherocketman/Microblogger</a>.</center></small>