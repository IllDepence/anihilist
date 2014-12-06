anihilist
=========
a ncurses client for anilist.co

![](http://moc.sirtetris.com/anihilist.gif)

features
--------
* display anilist.co watching list
* change number of watched episodes\*
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
anime list | **l** | increase watched episodes count by one\*
anime list | **h** | decrease watched episodes count by one\*
anime list | **i** | toggle ID layer
any list   | **s** | toggle XDCC layer
xdcc list  | **c** | toggle raw XDCC lines
xdcc list  | **y** | copy package number of current XDCC line to clipboard\*\*
any list   | **q** | quit

interface
---------
gui element      | meaning
---------------- | -------
`<title> '`      | entry in xdcc.json but no matches in retrieved packlist
`<title> *`      | entry in xdcc.json, matches in retrieved packlis, no unwatched eps
`<title> *<num>` | entry in xdcc.json, matches in retrieved packlis, `<num>` unwatched eps

\* planned, not yet implemented

\*\* requires xclip
