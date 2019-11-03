# The Static Site

* [Google Doc](https://docs.google.com/document/d/1sspMYXWc0_RRKZAnirpZpLZPckzBTo3MhUiZsIeQkXU/edit?ts=5dbe01a8#heading=h.ii5p04a61s9b)
* remap step in apatite that flattens data down to CSV, needs to become more nuanced because it make certain structures of data hard to express
  e.g. packaging data only returns if it's docker or snap or etc. should be a list instead of all valid packaging approaches
* metrics need to return dicts of tags with their confidence, first gen takes highest confidence, second gen returns all of them

# Fetching/pulling

* Fix outstanding git/hg/bzr clones, either with manual clone_urls or some other method (high pri)
  * viewvc
  * newspipe
* Add SVN support (low pri)
* split out "assets" in sloc (xml, svg, json, yaml, qml)
  * maybe docs too? md, tex, rst, org
  * tooling: autoconf, make, meson, Dockerfile
* update progress bar to say "(done)" instead of name of last project (wicd rn)
* tokei thinks .master = asp.net (also, ignore contrib, ignore vendor, ignore single files)
* "pure python" (need to separate out docs and other non-logical files detected by tokei)

# Stats Ideas

* presence of setup.py
* age / # of contributions, contributors. # of overlapping contributors.
* source control (git vs hg vs bzr)
* correlation between stars and contributors?
* Need to categorize small, medium, large
* Can committer distribution be used as an indicator of maturity?
* Can number of minor contributors be used as a proxy for popularity/usage?

# Data collection

* command to delete/archive results older than a certain date?
* apatite-results__2019-08-10T10-10-10__2019-08-10T10-10-10.json (oldest date__newest_date)
* apatite tarchive, apatite merge-tarchive ? (for cross-host results
  merging if repeating collection takes too long)
* probably add metric name to results file? (faster collation, not an issue now)
* Future: Make note of which data is missing when collating

## Licenses

Spotchecking the license output

* modoboa is actually ISC, not 0BSD (second guess)
* nvda is actually gplv2, under copying.txt (not bzip2)
* kallithea is actually GPLv3, not MPL
* 30 projects have no data (code is there for at least 15 of those)

# Tagsonomy improvements

* Console (and CLI/TUI/GUI) is more about UI than target platform
  * pgcli is a repl
  * chert is a CLI
  * term2048 is a TUI

# Interesting findings

* One of the apps (Meson) has its own sloc type
* One app has all its docs written in TeX

# apatite features

* Archiving
* utils to help backfill pypi links, wikipedia links, funding links
* metrics should live in list repo
* Stale projects (have not been updated for more than X% of their lifespan)

# More stats

* code of conduct
* contributor guidelines
* link stats (docs_link, etc.)
* Automation (detect tox, Makefile, scons, etc. usage)
  * 90 tox.inis (I'm used to seeing tox for libraries, not applications)
* i18n etc.
