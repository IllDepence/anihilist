anihilist
=========
a ncurses client for anilist.co

![](http://moc.sirtetris.com/anihilist.gif)

key features
------------
* display anilist.co anime lists
* change number of watched episodes
* move anime between lists
* search and add anime
* integration of xdcc lists

setup
-----
* write your anilist user[name|id] into the file `username`
* run `python3 anihilist.py`
* the program will ask you to generate an auth code on [this site](http://moc.sirtetris.com/anihilist/echocode.php)
* do so, paste it in the prompt, hit \<ENTER>
* from this point on, just run `python3 anihilist.py` to start anihilist

usage
-----
context    | key     | effect
---------- | ------- | ------
any list   | **k**   | navigate up
any list   | **j**   | navigate down
any list   | **q**   | quit
anime list | **1-5** | show watching&#124;completed&#124;plan to watch&#124;on hold&#124;dropped list
anime list | **i**   | toggle ID layer
anime list | **/**   | toggle search
anime list | **r**   | refresh XDCC info
anime list | **s**   | toggle XDCC layer
anime list | **l**   | increase watched episodes count by one
anime list | **h**   | decrease watched episodes count by one
anime list | **m**   | enter move mode (also used to add anime from search results)
xdcc list  | **c**   | toggle raw XDCC filenames
xdcc list  | **y**   | copy XDCC command to clipboard<sup>[1]</sup>
move mode  | **w&#124;c&#124;p&#124;h&#124;d** | move/add anime to watching&#124;completed&#124;plan to watch&#124;on hold&#124;dropped list
move mode  | **[^wcphd]** | leave move mode

[1] requires [xclip](http://linux.die.net/man/1/xclip)

interface
---------
gui element      | meaning
---------------- | -------
`^<title> '`     | entry in xdcc.json but no matches in retrieved packlists
`^<title> *`     | entry in xdcc.json, matches in retrieved packlists, no unwatched eps
`^<title> *<num>`| entry in xdcc.json, matches in retrieved packlists, `<num>` unwatched eps
[w&#124;c&#124;p&#124;h&#124;d]$   | anime under cursor is in move mode

xdcc integration
----------------
xdcc integration is tailored towards the output of a piece of software called *XDCC Parser*.

the file `xdcc.json` contains two arrays. `anime` for anime (duh) and `sources` for xdcc packlists. an anime entry requires a title (as it appears in a packlist), a subgroup and the anilist id (that's what the ID layer is good for). all source entries are set to inactive by default to keep startup time minimal for people not using the xdcc integration.

planned features
----------------
* remove anime
