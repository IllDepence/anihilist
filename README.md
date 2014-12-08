anihilist
=========
a ncurses client for anilist.co

![](http://moc.sirtetris.com/anihilist.gif)

features
--------
* display anilist.co anime lists
* change number of watched episodes<sup>[1]</sup>
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
context    | key   | effect
---------- | ----- | ------
any list   | **k** | navigate up
any list   | **j** | navigate down
any list   | **q** | quit
anime list | **1-5** | show watching&#124;completed&#124;plan to watch&#124;on hold&#124;dropped list
anime list | **i** | toggle ID layer
xdcc list  | **c** | toggle raw XDCC lines
xdcc list  | **y** | copy package number of current XDCC line to clipboard<sup>[2]</sup>
any anime  | **l** | increase watched episodes count by one<sup>[1]</sup>
any anime  | **h** | decrease watched episodes count by one<sup>[1]</sup>
anime \*   | **s** | toggle XDCC layer

interface
---------
gui element      | meaning
---------------- | -------
`<title> '`      | entry in xdcc.json but no matches in retrieved packlist
`<title> *`      | entry in xdcc.json, matches in retrieved packlis, no unwatched eps
`<title> *<num>` | entry in xdcc.json, matches in retrieved packlis, `<num>` unwatched eps

xdcc integration
----------------
look at the file `xdcc.json`, it's pretty self explanatory. for each anime fill in a url to a packlist, a title and group to search for and the anilist id (that's what the ID layer is good for).

---

[1] planned, not yet implemented

[2] requires xclip
