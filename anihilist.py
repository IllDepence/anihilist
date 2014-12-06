# -*- coding: utf-8 -*-

import curses
import http.client
import json
import os
import re
import time
import unicodedata
import urllib.request
from sys import stdin

NAV_U       = 'k'
NAV_D       = 'j'
NAV_L       = 'h'
NAV_R       = 'l'
CLIENT_ID   = 'sirtetris-eky4q'
CLIENT_SEC  = None
USER        = None
REDIR_FOO   = 'http%3A%2F%2Fmoc.sirtetris.com%2Fanihilist%2Fechocode.php'
DISP_KEY    = None
SORT_KEY    = None
ID_MODE     = False

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

def getAuthCode():
    print('You have to generate an auth code:\n'
          'http://moc.sirtetris.com/anihilist/echocode.php\n\n'
          'Paste it here, then continue with <ENTER>.')
    return stdin.readline().strip()

def setup():
    setUser()
    setClientSecret()
    if not os.path.exists('access_data.json'):
        auth_code = getAuthCode()
        newAccessToken(auth_code)
    else:
        getAccessToken() # may have to be refreshed

def callAPI(method, url, data=None):
    conn = http.client.HTTPSConnection('anilist.co', 443)
    conn.request(method=method, url=url, body=data)
    resp_obj = conn.getresponse()
    resp_json = resp_obj.read().decode('utf-8')
    resp_data = json.loads(resp_json)
    return resp_data

def newAccessToken(auth_code):
    url = ('/api/auth/access_token?grant_type=authorization_code'
           '&client_id={0}&client_secret={1}&redirect_uri={2}'
           '&code={3}').format(CLIENT_ID,CLIENT_SEC,REDIR_FOO,auth_code)
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
    url = ('/api/user/{0}/animelist?access_token='
           '{1}').format(USER, getAccessToken())
    return callAPI('GET', url)

def cursesShutdown():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def addListLine(scr, y, x_max, anime):
    title = getTitle(anime)
    ep_total = anime['anime']['total_episodes']
    if ep_total == 0: ep_total = '?'
    ep_seen = anime['episodes_watched']
    ep_info = ' [{0}/{1}]'.format(ep_seen,ep_total)
    scr.addstr(y, 0, ' '*x_max)
    scr.addstr(y, 0, title)
    scr.addstr(y, (x_max-len(ep_info)), ep_info)

def getTitle(anime):
    global ID_MODE
    global DISP_KEY
    global SORT_KEY
    if ID_MODE:
        return str(anime['anime']['id']).strip()
    else:
        return anime['anime'][DISP_KEY].strip()

def printList(scr, anime_watching, selected, offset):
    (y_max,x_max)=scr.getmaxyx()
    anime_watchings = sorted(anime_watching,
                             key=lambda k: k['anime'][SORT_KEY])
    y=0
    while y+1<y_max and y+offset<len(anime_watchings):
        anime = anime_watchings[y+offset]
        if selected == y:
            scr.standout()
            addListLine(scr, y, x_max, anime)
            scr.standend()
        else:
            addListLine(scr, y, x_max, anime)
        y+=1

def setListLanguage(anime_list_data):
    global DISP_KEY
    global SORT_KEY

    if anime_list_data['title_language'] == 'japanese':
        DISP_KEY = 'title_japanese'
        SORT_KEY = 'title_romaji'
    elif anime_list_data['title_language'] == 'romaji':
        DISP_KEY = 'title_romaji'
        SORT_KEY = 'title_romaji'
    else:
        DISP_KEY = 'title_english'
        SORT_KEY = 'title_english'

def toggleIDs(anime_list_data):
    global ID_MODE
    ID_MODE = not ID_MODE

def getXDCCInfo():
    # xdcc.json file
    with open('xdcc.json', 'r') as f:
        xdcc_json = f.read().rstrip()
    f.close()
    xdcc_local_data = json.loads(xdcc_json)
    urls = []
    # get packlist data
    for entry in xdcc_local_data:
        if not entry['url'] in urls:
            urls.append(entry['url'])
    xdcc_lists = {}
    for url in urls:
        xdcc_lists[url] = str(urllib.request.urlopen(url).read(), 'utf-8')
    # build xdcc info package
    xdcc_info = {}
    for entry in xdcc_local_data:
        key = entry['al_id']
        group = entry['group']
        title = entry['packlist_title']
        patt = re.compile('^#(([0-9]+).+?\[{0}].+?{1}'       # pack num & title
                          '[^\[\(0-9]+?'                     # not [ ( 0-9
                          '([0-9]+).*$)'.format(group, title), re.M) # ep num
        xdcc_text = xdcc_lists[entry['url']]
        matches = re.findall(patt, xdcc_text)
        pkgs = []
        for m in matches:
            pkg = {}
            pkg['line'] = m[0]
            pkg['pkg_num'] = m[1]
            pkg['ep_num'] = m[2]
            pkgs.append(pkg)
        xdcc_info[key] = pkgs
    return xdcc_info

def main(stdscr):
    anime_list_data = getAnimeList()
    setListLanguage(anime_list_data)
    anime_lists = anime_list_data['lists']
    anime_watching = anime_lists['watching']

    xdcc_info = getXDCCInfo()

    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.clear()
    (y_max,x_max)=stdscr.getmaxyx()
    y_max_nav = min((len(anime_watching)-1), y_max-2)
    list_max_nav = len(anime_watching)-1
    curs_y=0
    offset=0
    c=None

    while c != 'q':
        stdscr.move(0,0)
        printList(stdscr, anime_watching, curs_y, offset)
        c = stdscr.getkey()
        if c==NAV_U:
            if curs_y==0 and offset != 0:
                offset-=1
            elif curs_y>0:
                curs_y-=1
        if c==NAV_D:
            if curs_y<y_max_nav:
                curs_y+=1
            elif curs_y+offset<list_max_nav:
                offset+=1
        if c==NAV_L:
            pass
        if c==NAV_R:
            pass
        if c=='i':
            toggleIDs(anime_list_data)

if __name__ == '__main__':
    setup()
    curses.wrapper(main)
