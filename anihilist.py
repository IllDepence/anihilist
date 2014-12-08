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
LIST_ANIME  = 0
LIST_XDCC   = 1
UP          = -1
DOWN        = 1

class TheScreen:
    def set(src):
        TheScreen.src = src
    def get():
        return TheScreen.src

class Anime:
    def __init__(self, al_data, xdcc_info, parent):
        self.al_id = str(al_data['anime']['id'])
        self.parent = parent
        self.title = {}
        self.title['ja'] = al_data['anime']['title_japanese'].strip()
        self.title['en'] = al_data['anime']['title_english'].strip()
        self.title['ro'] = al_data['anime']['title_romaji'].strip()
        ep_total = al_data['anime']['total_episodes']
        if ep_total > 0:
            self.ep_total = str(ep_total)
        else:
            self.ep_total = '?'
        self.ep_seen = str(al_data['episodes_watched'])
        self.pkg_list = None
        if self.al_id in xdcc_info:
            pkg_list_raw = xdcc_info[self.al_id]
            pkg_list_arg = []
            for pkg in pkg_list_raw:
                pkg.seen = (int(pkg.ep_num) <= int(self.ep_seen))
                pkg_list_arg.append(pkg)
            self.pkg_list = PackageList(pkg_list_arg, self)
            self._set_xdcc_cue(pkg_list_raw)
        else:
            self.xdcc_cue = ''
    def _set_xdcc_cue(self, pkg_list_raw):
        ep_nums = [int(pkg.ep_num) for pkg in pkg_list_raw]
        if len(ep_nums) > 0:
            ep_newest = max(ep_nums)
        else:
            ep_newest = 0
        ep_seen = int(self.ep_seen)
        if ep_newest > ep_seen:
            self.xdcc_cue = '*' + str(ep_newest-ep_seen)
        elif ep_newest > 0:
            self.xdcc_cue = '*'
        else:
            self.xdcc_cue = '\''

class Package():
    def __init__(self, ep_num, pkg_num, group, line, seen):
        self.ep_num = ep_num
        self.pkg_num = pkg_num
        self.group = group
        self.line = line
        self.seen = seen

class List:
    def __init__(self, lisd):
        self.scr = TheScreen.get()
        self.lisd = lisd
        self.cursor = 0
        self.offset = 0
        (y_max,x_max) = self.scr.getmaxyx()
        self.end_screen = y_max-2
        self.x_max = x_max
        self.end_list = len(lisd)-1
    def __len__(self):
        return len(self.lisd)
    def _getOnScreen(self):
        start_idx = self.offset
        end_idx = min(self.end_screen, self.end_list) + self.offset
        return self.lisd[start_idx:(end_idx+1)]
    def scroll(self, delta):
        goal_screen = self.cursor + delta
        goal_list = self.cursor + self.offset + delta
        if goal_list>self.end_list:
            return
        elif goal_screen<0:
            if self.offset==0:
                return
            else:
                self.offset += delta
        elif goal_screen>self.end_screen:
            self.offset += delta
        else:
            self.cursor += delta
    def getUnderCursor(self):
        return self.lisd[self.cursor + self.offset]

class AnimeList(List):
    def __init__(self, anilist_data, list_key, xdcc_info):
        self.anilist_data = anilist_data
        self.list_key = list_key
        self.xdcc_info = xdcc_info
        self.id_mode = False
        self._setListLanguage()
        self._updateEntries()
    def _updateEntries(self):
        list_raw = self.anilist_data['lists'][self.list_key]
        list_processed = []
        for al_data in list_raw:
            list_processed.append(Anime(al_data, self.xdcc_info, self))
        sortd = sorted(list_processed, key=lambda k: k.title[self.sort_key])
        List.__init__(self, sortd)
    def toggleIDMode(self):
        self.id_mode = not self.id_mode
    def setListKey(self, key):
        self.list_key = key
        self._updateEntries()
        self.scr.clear()
    def display(self):
        sub_list = self._getOnScreen()
        y = 0
        for anime in sub_list:
            if self.cursor == y: self.scr.standout()
            self._addListLine(y, anime)
            if self.cursor == y: self.scr.standend()
            y+=1
    def _addListLine(self, y, anime):
        title = self._getTitle(anime)
        ep_info = ' [{0}/{1}]'.format(anime.ep_seen, anime.ep_total)
        self.scr.addstr(y, 0, ' '*self.x_max)
        self.scr.addstr(y, 0, title)
        self.scr.addstr(y, (self.x_max-len(ep_info)), ep_info)
    def _getTitle(self, anime):
        if self.id_mode:
            return anime.al_id
        else:
            return anime.title[self.title_key] + ' ' + anime.xdcc_cue
    def _setListLanguage(self):
        if self.anilist_data['title_language'] == 'japanese':
            self.title_key = 'ja'
            self.sort_key = 'ro'
        elif self.anilist_data['title_language'] == 'romaji':
            self.title_key = 'ro'
            self.sort_key = 'ro'
        else:
            self.title_key = 'en'
            self.sort_key = 'en'

class PackageList(List):
    def __init__(self, pkgs, parent):
        self.parent = parent
        self.raw_mode = False
        sortd = sorted(pkgs, key=lambda k: k.ep_num)
        List.__init__(self, sortd)
    def toggleRawMode(self):
        self.raw_mode = not self.raw_mode
    def yankUnderCursor(self):
        pkg = self.getUnderCursor()
        try:
            os.system('echo -n "{0}" | xclip'.format(pkg.pkg_num))
        except:
            pass
    def display(self):
        sub_list = self._getOnScreen()
        y = 0
        for pkg in sub_list:
            idx = y + self.offset
            anime = self.parent
            anime_list = anime.parent
            if self.raw_mode:
                line = pkg.line
            else:
                title = anime.title[anime_list.title_key]
                line = '{0} -> [{1}] {2} {3}'.format(pkg.pkg_num, pkg.group,
                                title, pkg.ep_num)
            if int(pkg.ep_num) > int(anime.ep_seen):
                self.scr.standout()
            self.scr.addstr(y, 0, ' '*self.x_max)
            if self.cursor == y:
                self.scr.addstr(y, 0, '- ' + line)
            else:
                self.scr.addstr(y, 0, '  ' + line)
            y+=1
        self.scr.standend()

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

def callAPI(method, url, data=None, headers={}):
    import pprint
    if(method=='PUT'):
        with open('debug', 'w') as f:
            #pprint.pprint(data, f)
            f.write(data)
        f.close()
    conn = http.client.HTTPSConnection('anilist.co', 443)
    conn.request(method=method, url=url, body=data, headers=headers)
    resp_obj = conn.getresponse()
    resp_json = resp_obj.read().decode('utf-8')
    if(method=='PUT'):
        with open('debug2', 'w') as f:
            #pprint.pprint(resp_data, f)
            f.write(resp_json)
        f.close()
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

def updateWatchedCount(anime, delta):
    old = int(anime.ep_seen)
    new = old+delta
    a_id = int(anime.al_id)
    url = '/api/animelist'
    data = urllib.parse.urlencode({'id':a_id, 'episodes_watched':new})
    headers = {}
    headers['Authorization'] = 'bearer {0}'.format(getAccessToken())
    return callAPI('PUT', url, data=data, headers=headers)

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
            pkgs.append(Package(m[2], m[1], entry['group'], m[0], None))
        xdcc_info[key] = pkgs
    return xdcc_info

def getUpdatedAnimeList():
    anilist_data = getAnimeList()
    xdcc_info = getXDCCInfo()
    return AnimeList(anilist_data, 'watching', xdcc_info)

def main(stdscr):
    TheScreen.set(stdscr)
    anime_list = getUpdatedAnimeList()

    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.clear()

    c=None
    list_type=LIST_ANIME

    while c != 'q':
        stdscr.move(0,0)
        anime_curs = anime_list.getUnderCursor()

        if list_type==LIST_ANIME:
            anime_list.display()
        elif list_type==LIST_XDCC:
            anime_curs.pkg_list.display()

        c = stdscr.getkey()
        if c==NAV_U:
            if list_type == LIST_ANIME:
                anime_list.scroll(UP)
            if list_type == LIST_XDCC:
                anime_curs.pkg_list.scroll(UP)
        if c==NAV_D:
            if list_type == LIST_ANIME:
                anime_list.scroll(DOWN)
            if list_type == LIST_XDCC:
                anime_curs.pkg_list.scroll(DOWN)
        if c==NAV_L:
            pass
        if c==NAV_R:
            pass
            #updateWatchedCount(anime_curs, 1)
            #anime_list = getUpdatedAnimeList()
        if c=='1' and list_type==LIST_ANIME:
            anime_list.setListKey('watching')
        if c=='2' and list_type==LIST_ANIME:
            anime_list.setListKey('completed')
        if c=='3' and list_type==LIST_ANIME:
            anime_list.setListKey('plan_to_watch')
        if c=='4' and list_type==LIST_ANIME:
            anime_list.setListKey('on_hold')
        if c=='5' and list_type==LIST_ANIME:
            anime_list.setListKey('dropped')
        if c=='i' and list_type==LIST_ANIME:
            anime_list.toggleIDMode()
        if c=='c' and list_type==LIST_XDCC:
            anime_curs.pkg_list.toggleRawMode()
        if c=='y' and list_type==LIST_XDCC:
            anime_curs.pkg_list.yankUnderCursor()
        if c=='s' and not anime_curs.pkg_list is None and len(anime_curs.pkg_list)>0:
            stdscr.clear()
            list_type = 1-list_type

if __name__ == '__main__':
    setup()
    curses.wrapper(main)
