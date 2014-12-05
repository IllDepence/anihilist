# -*- coding: utf-8 -*-

import curses
import http.client
import json
import sqlite3
import sys
import unicodedata

NAV_U='k'
NAV_D='j'
NAV_L='h'
NAV_R='l'
CLIENT_ID='sirtetris-eky4q'
with open('client_secret', 'r') as f:
    CLIENT_SEC=f.read().rstrip()
f.close()
#http://moc.sirtetris.com/anihilist/echocode.php
AUTH_CODE='yJ3KkwydvQ5Q05aAikGApEJPXTaPrPXSDQU84K06'
REDIR_FOO='http%3A%2F%2Fmoc.sirtetris.com%2Fanihilist%2Fechocode.php'

def cursesShutdown():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def getAccessToken():
    conn = http.client.HTTPSConnection('anilist.co', 443)
    url = ('/api/auth/access_token?grant_type=authorization_code'
           '&client_id={0}&client_secret={1}&redirect_uri={2}'
           '&code={3}').format(CLIENT_ID,CLIENT_SEC,REDIR_FOO,AUTH_CODE)
    conn.request(method='POST', url=url)
    resp_obj = conn.getresponse()
    json_text = resp_obj.read().decode('utf-8')
    resp_data = json.loads(json_text)
    return resp_data['access_token']

def main(stdscr):
    token = getAccessToken()

    stdscr.clear()
    (y_max,x_max)=stdscr.getmaxyx()
    y_max-=1
    x_max-=1
    x=0
    y=0
    while True:
        stdscr.clear()
        stdscr.addstr(y,x,str(token))
        c = stdscr.getkey()
        if(c==NAV_U and y>0):
            y-=1
        if(c==NAV_D and y<y_max):
            y+=1
        if(c==NAV_L and x>0):
            x-=1
        if(c==NAV_R and x<x_max):
            x+=1

if __name__ == '__main__':
    curses.wrapper(main)
