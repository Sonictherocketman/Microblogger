# Microblogger

*IN DEV: See issues*

A basic microblogging service implementing the [Open Microblog][1] standard. It is intended to be a base implementation of the standard; a proof of concept for the standard.

[1]: https://github.com/Sonictherocketman/Open-Microblog

**For detailed information, [see our new Wiki](https://github.com/Sonictherocketman/Microblogger/wiki)!**

## About Microblogger

Short version: Its like Twitter, but you host your account on your own computer (preferably a server). You can talk to anyone else using Microblogger or any other person using [Open Microblog][1] compatable program. All your data is kept on your server and you have control over all of it.

Long version: *inhales* Here we go...

Microblogger is a single-user web-app that allows users to host their own microblog, communicate with others using Microblogger (or other compatable service). As the first implementation of the Open Microblog standard, Microblogger's aim is to be 100% standards compliant. That means that users can expect to be able to:

    - Follow other users
    - Message and conversate with other users in a similar manner to Twitter
    - Post short messages to the public or to friends
    - Share links
    - Block unwanted users and share who they block with their friends (i.e. communal blocking)
    - Migrate between services without losing followers or settings
    - Keep a local archive of everything they post (since they control the files anyway)

## Installing Microblogger

Currently, the preferred way to install Microblogger is:

    1. Clone the Git Repo, or download it as a zip
    2. Extract the repo to '/var/www/' (UNIX systems only)
    3. Make sure you have all the dependencies
        - microblogcrawler
        - Flask
        - etc (Full list coming soon)
        * All of the dependencies can be installed with pip
    4. Open your favorite terminal and type `python microblogger.py`

Pull requests gladly accepted.
