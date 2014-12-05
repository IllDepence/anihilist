# -*- coding: utf-8 -*-

import curses
import http.client
import json
import os
import time
import unicodedata

NAV_U       = 'k'
NAV_D       = 'j'
NAV_L       = 'h'
NAV_R       = 'l'
CLIENT_ID   = 'sirtetris-eky4q'
CLIENT_SEC  = None
AUTH_CODE   = None
USER        = None
REDIR_FOO   = 'http%3A%2F%2Fmoc.sirtetris.com%2Fanihilist%2Fechocode.php'

def setUser():
    global USER
    with open('username', 'r') as f:
        USER = f.read().rstrip()
    f.close()

def setClientSecret():
    global CLIENT_SEC
    with open('client_secret', 'r') as f:
        CLIENT_SEC = f.read().rstrip()
    f.close()

def setAuthCode():
    global AUTH_CODE
    with open('auth_code', 'r') as f:
        auth_file_contents = f.read().rstrip()
    f.close()
    if len(auth_file_contents) == 0:
        print('You have to generate an auth code:\n'
              'http://moc.sirtetris.com/anihilist/echocode.php\n\n'
              'Save it in the file auth_code, then press any key.')
        input()
        setAuthCode()
    else:
        AUTH_CODE = auth_file_contents
        with open('auth_code', 'w') as f:
            f.write('')
        f.close()

def setup():
    setUser()
    setClientSecret()
    if not os.path.exists('access_data.json'):
        setAuthCode()
        newAccessToken()
    else:
        getAccessToken() # may have to be refreshed

def callAPI(method, url, data=None):
    conn = http.client.HTTPSConnection('anilist.co', 443)
    conn.request(method=method, url=url, body=data)
    resp_obj = conn.getresponse()
    resp_json = resp_obj.read().decode('utf-8')
    resp_data = json.loads(resp_json)
    return resp_data

def newAccessToken():
    url = ('/api/auth/access_token?grant_type=authorization_code'
           '&client_id={0}&client_secret={1}&redirect_uri={2}'
           '&code={3}').format(CLIENT_ID,CLIENT_SEC,REDIR_FOO,AUTH_CODE)
    access_data = callAPI('POST', url)
    with open('access_data.json', 'w') as f:
        f.write(json.dumps(access_data))
    f.close()

def getAccessToken():
    with open('access_data.json', 'r') as f:
        access_json = f.read().rstrip()
    f.close()
    access_data = json.loads(access_json)
    now = int(time.time())
    if (now+60) > access_data['expires']:
        return refreshAccessToken(access_data['refresh_token'])
    else:
        return access_data['access_token']

def refreshAccessToken(refresh_token):
    url = ('/api/auth/access_token?grant_type=refresh_token'
           '&client_id={0}&client_secret={1}&refresh_token='
           '{2}').format(CLIENT_ID,CLIENT_SEC,refresh_token)
    access_data_new = callAPI('POST', url)
    with open('access_data.json', 'r+') as f:
        access_json = f.read().rstrip()
        access_data = json.loads(access_json)
        access_data['access_token'] = access_data_new['access_token']
        access_data['expires'] = access_data_new['expires']
        f.seek(0)
        f.truncate()
        f.write(json.dumps(access_data))
    f.close()
    return access_data['access_token']

def getAnimeList():
    #TODO: maybe switch back to /raw as soon as titles are included
    url = ('/api/user/{0}/animelist?access_token='
           '{1}').format(USER, getAccessToken())
    return callAPI('GET', url)

def cursesShutdown():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def addListLine(stdscr, y, x_max, anime):
    title = anime['anime']['title_japanese']
    ep_total = anime['anime']['total_episodes']
    if ep_total == 0: ep_total = '?'
    ep_seen = anime['episodes_watched']
    ep_info = ' [{0}/{1}]'.format(ep_seen,ep_total)
    stdscr.addstr(y, 0, title)
    stdscr.addstr(y, (x_max-len(ep_info)), ep_info)

#def main():
def main(stdscr):
    setup()
    anime_list_data = getAnimeList()
    anime_lists = anime_list_data['lists']
    anime_watching = anime_lists['watching']

    curses.curs_set(0)
    stdscr.clear()
    (y_max,x_max)=stdscr.getmaxyx()
    y_max-=1
    x_max-=1
    x=0
    y=0
    stdscr.clear()
    for anime in anime_watching:
        addListLine(stdscr, y, x_max, anime)
        y+=1

    while True:
        stdscr.addstr(y,x,'X')
        c = stdscr.getkey()
        if(c==NAV_U and y>0):
            y-=1
        if(c==NAV_D and y<y_max):
            y+=1
        if(c==NAV_L and x>0):
            x-=1
        if(c==NAV_R and x<x_max):
            x+=1
    #window.scroll([lines=1]) !!!

if __name__ == '__main__':
    curses.wrapper(main)

#if __name__ == '__main__':
#    main()
