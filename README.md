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
xdcc list  | **c**   | toggle raw XDCC lines
xdcc list  | **y**   | copy package number of current XDCC line to clipboard<sup>[1]</sup>
move mode  | **w&#124;c&#124;p&#124;h&#124;d** | move/add anime to watching&#124;completed&#124;plan to watch&#124;on hold&#124;dropped list
move mode  | **[^wcphd]** | leave move mode

[1] requires [xclip](http://linux.die.net/man/1/xclip)

interface
---------
gui element      | meaning
---------------- | -------
`^<title> '`     | entry in xdcc.json but no matches in retrieved packlist
`^<title> *`     | entry in xdcc.json, matches in retrieved packlis, no unwatched eps
`^<title> *<num>`| entry in xdcc.json, matches in retrieved packlis, `<num>` unwatched eps
`[w|c|p|h|d]$`   | anime under cursor is in move mode

xdcc integration
----------------
look at the file `xdcc.json`, it's pretty self explanatory. for each anime fill in a url to a packlist, a title and group to search for and the anilist id (that's what the ID layer is good for).

planned features
----------------
* change rating of anime
* make anime search compatible with japanese input
