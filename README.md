anihilist
=========
a ncurses client for anilist.co

![](http://moc.sirtetris.com/anihilist.png)

features
--------
* display anilist.co watching list
* change number of watched episodes

setup
-----
* write your anilist user[name|id] into the file `username`
* run `python3 anihilist.py`
* the programm will ask you to generate an auth code on [this site](http://moc.sirtetris.com/anihilist/echocode.php), do so
* paste auth code into file `auth_code`, press any key
* from this point on, just run `python3 anihilist.py` to start anihilist

usage
-----
* **k** -> navigate up
* **j** -> navigate down
* **l** -> increase watched episodes count by one
* **h** -> decrease watched episodes count by one
