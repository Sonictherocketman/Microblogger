# Twitter Archive -> RSS Microblog Conversion

- Download CSV
- using top row as tag names, create XML file
- convert the following:
	- tweet_id -> guid + isPermalink='false'
	- add language to each item
	- text -> description
	- timestamp -> pubDate
	- change guide to something truly random
	- generate a truly unique id string

# Notes

- Use only standard RSS tags when possible.
- encapsulate HTML elements in <![CDATA[]]> tags.
- need new tags for reply to and reposted
- Posts *should* be limited to 200 characters to keep an item entry below 1KB (~915 Bytes) (UTF-8).