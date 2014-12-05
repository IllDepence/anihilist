anihilist
=========
a ncurses client for anilist.co

![](http://moc.sirtetris.com/anihilist.png)

NOTE
----
this repository does not include the file `client_secret`, which is needed for the program to operate. for now the only option to use it is to set up a [client](http://anilist.co/developer) yourself, use the redirect URL `http://moc.sirtetris.com/anihilist/echocode.php` and change the `CLIENT_ID` in `anihilist.py` according to the values on anilist.co.

features
--------
* display anilist.co watching list
* change number of watched episodes\*

setup
-----
* write your anilist user[name|id] into the file `username`
* run `python3 anihilist.py`
* the program will ask you to generate an auth code on [this site](http://moc.sirtetris.com/anihilist/echocode.php), do so
    paste it in the prompt, hit \<ENTER>
* from this point on, just run `python3 anihilist.py` to start anihilist

usage
-----
* **q** -> exit the program
* **k** -> navigate up
* **j** -> navigate down
* **l** -> increase watched episodes count by one\*
* **h** -> decrease watched episodes count by one\*

\* planned, not yet implemented
