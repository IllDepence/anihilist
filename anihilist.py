# -*- coding: utf-8 -*-

import curses
import http.client
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import sys

NAV_U       = 'k'
NAV_D       = 'j'
NAV_L       = 'h'
NAV_R       = 'l'
CLIENT_ID   = 'sirtetris-eky4q'
CLIENT_SEC  = 'AcF5qNj4St50Bf0mPLLU9BgpRObb'
USER        = None
REDIR_FOO   = 'http%3A%2F%2Fmoc.sirtetris.com%2Fanihilist%2Fechocode.php'
DISP_KEY    = None
SORT_KEY    = None
ID_MODE     = False
RAW_MODE    = False
LIST_ANIME  = 0
LIST_XDCC   = 1

def setUser():
    global USER
    with open('username', 'r') as f:
        USER = f.read().rstrip()
    f.close()

def getAuthCode():
    print('You have to generate an auth code:\n'
          'http://moc.sirtetris.com/anihilist/echocode.php\n\n'
          'Paste it here, then continue with <ENTER>.')
    return sys.stdin.readline().strip()

def setup():
    setUser()
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
    #import pprint
    #with open('debug', 'w') as f:
    #    pprint.pprint(resp_data, f)
    #    #f.write(data)
    #f.close()
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

def updateWatchedCount(anime, delta):
    old = int(anime['episodes_watched'])
    new = old+delta
    a_id = int(anime['anime']['id'])
    url = ('/api/animelist?access_token='
           '{1}').format(USER, getAccessToken())
    data = urllib.parse.urlencode({'id':a_id,
                                   'list_status':'watching',
                                   'score':6.5,
                                   'episodes_watched':new,
                                   'rewatched':anime['rewatched'],
                                   'notes':anime['notes'],
                                   'advanced_rating_scores':'',
                                   'custom_lists':'',
                                   'hidden_default':''})
    return callAPI('PUT', url, data=data)

def cursesShutdown():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def addListLine(scr, y, x_max, anime, xdcc_info):
    title = getTitle(anime, xdcc_info)
    ep_total = anime['anime']['total_episodes']
    if ep_total == 0: ep_total = '?'
    ep_seen = anime['episodes_watched']
    ep_info = ' [{0}/{1}]'.format(ep_seen,ep_total)
    scr.addstr(y, 0, ' '*x_max)
    scr.addstr(y, 0, title)
    scr.addstr(y, (x_max-len(ep_info)), ep_info)

def getTitle(anime, xdcc_info):
    a_id = str(anime['anime']['id'])
    if ID_MODE:
        return a_id
    else:
        title = anime['anime'][DISP_KEY].strip()
        if a_id in xdcc_info:
            return XDCCTitle(anime, title, xdcc_info[a_id])
        else:
            return title

def XDCCTitle(anime, title, pkgs):
    ep_nums = [int(pkg['ep_num']) for pkg in pkgs]
    if len(ep_nums) > 0:
        ep_newest = max(ep_nums)
    else:
        ep_newest = 0
    ep_seen = int(anime['episodes_watched'])
    if ep_newest > ep_seen:
        return title + ' *' + str(ep_newest-ep_seen)
    elif ep_newest > 0:
        return title + ' *'
    else:
        return title + ' \''

def printList(scr, anime_watchings, selected, offset, xdcc_info):
    (y_max,x_max)=scr.getmaxyx()
    y=0
    while y+1<y_max and y+offset<len(anime_watchings):
        anime = anime_watchings[y+offset]
        if selected == y:
            scr.standout()
            addListLine(scr, y, x_max, anime, xdcc_info)
            scr.standend()
        else:
            addListLine(scr, y, x_max, anime, xdcc_info)
        y+=1

def printPkgList(scr, anime, selected, xdcc_info, offset):
    (y_max,x_max)=scr.getmaxyx()
    ep_seen = int(anime['episodes_watched'])
    pkgs = xdcc_info[str(anime['anime']['id'])]
    pkgss = sorted(pkgs, key=lambda k: k['ep_num'])
    y=0
    while y+1<y_max and y+offset<len(pkgss):
        pkg = pkgss[y+offset]
        if RAW_MODE:
            line = pkg['line']
        else:
            line = '{0} -> [{1}] {2} {3}'.format(pkg['pkg_num'], pkg['group'],
                            anime['anime'][DISP_KEY].strip(), pkg['ep_num'])
        if int(pkg['ep_num']) > ep_seen:
            scr.standout()
        scr.addstr(y, 0, ' '*x_max)
        if selected == y:
            scr.addstr(y, 0, '- ' + line)
        else:
            scr.addstr(y, 0, '  ' + line)
        y+=1
    scr.standend()

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

def toggleIDs():
    global ID_MODE
    ID_MODE = not ID_MODE

def toggleRAW():
    global RAW_MODE
    RAW_MODE = not RAW_MODE

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
            pkg['group'] = entry['group']
            pkgs.append(pkg)
        xdcc_info[key] = pkgs
    return xdcc_info

def updateAnimeWatchings(anime_list_data):
    setListLanguage(anime_list_data)
    anime_lists = anime_list_data['lists']
    anime_watching = anime_lists['watching']
    anime_watchings = sorted(anime_watching,
                             key=lambda k: k['anime'][SORT_KEY])
    return anime_watchings

def XDCCNavLimit(anime, xdcc_info):
    key = str(anime['anime']['id'])
    if key in xdcc_info:
        pkgs = xdcc_info[key]
        return len(pkgs)
    else:
        return 0

def yankXDCC(xdcc_info, xdcc_key, idx):
    pkgs = xdcc_info[xdcc_key]
    pkg_num = pkgs[idx]['pkg_num']
    try:
        os.system('echo -n "{0}" | xclip'.format(pkg_num))
    except:
        pass

def main(stdscr):
    anime_watchings = updateAnimeWatchings(getAnimeList())
    xdcc_info = getXDCCInfo()

    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.clear()
    (y_max,x_max)=stdscr.getmaxyx()

    y_max_nav=[None]*2
    y_max_nav[LIST_ANIME] = min((len(anime_watchings)-1), y_max-2)
    list_max_nav=[None]*2
    list_max_nav[LIST_ANIME] = len(anime_watchings)-1
    curs_y=[None]*2
    curs_y[LIST_ANIME]=0
    curs_y[LIST_XDCC]=0
    offset=[None]*2
    offset[LIST_ANIME]=0
    offset[LIST_XDCC]=0

    c=None
    list_type=0

    while c != 'q':
        stdscr.move(0,0)
        anime_curs = anime_watchings[curs_y[LIST_ANIME]+offset[LIST_ANIME]]
        xdcc_key = str(anime_curs['anime']['id'])

        if list_type==LIST_ANIME:
            printList(stdscr, anime_watchings, curs_y[LIST_ANIME],
                            offset[LIST_ANIME], xdcc_info)
        elif list_type==LIST_XDCC:
            printPkgList(stdscr, anime_curs, curs_y[LIST_XDCC], xdcc_info,
                            offset[LIST_XDCC])

        c = stdscr.getkey()
        if c==NAV_U:
            if curs_y[list_type]==0 and offset[list_type] != 0:
                offset[list_type]-=1
            elif curs_y[list_type]>0:
                curs_y[list_type]-=1
        if c==NAV_D:
            if curs_y[list_type]<y_max_nav[list_type]:
                curs_y[list_type]+=1
            elif curs_y[list_type]+offset[list_type]<list_max_nav[list_type]:
                offset[list_type]+=1
        if c==NAV_L:
            pass
        if c==NAV_R:
            pass
            #updateWatchedCount(anime_curs, 1)
            #anime_watchings = updateAnimeWatchings(getAnimeList())
        if c=='i' and list_type==LIST_ANIME:
            toggleIDs()
        if c=='c' and list_type==LIST_XDCC:
            toggleRAW()
        if c=='y' and list_type==LIST_XDCC:
            yankXDCC(xdcc_info, xdcc_key, curs_y[LIST_XDCC])
        if c=='s' and xdcc_key in xdcc_info:
            stdscr.clear()
            list_type = 1-list_type
            curs_y[LIST_XDCC]=0
            offset[LIST_XDCC]=0
            pkg_count = XDCCNavLimit(anime_curs, xdcc_info)
            list_max_nav[LIST_XDCC] = pkg_count-1
            y_max_nav[LIST_XDCC] = min(pkg_count-1, y_max-2)

if __name__ == '__main__':
    setup()
    curses.wrapper(main)
