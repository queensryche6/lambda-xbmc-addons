# -*- coding: utf-8 -*-

'''
    Viooz XBMC Addon
    Copyright (C) 2014 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib,urllib2,re,os,threading,datetime,time,base64,xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
from operator import itemgetter
try:    import json
except: import simplejson as json
try:    import CommonFunctions
except: import commonfunctionsdummy as CommonFunctions
try:    import StorageServer
except: import storageserverdummy as StorageServer
from metahandler import metahandlers
from metahandler import metacontainers



action              = None
common              = CommonFunctions
metaget             = metahandlers.MetaData(preparezip=False)
language            = xbmcaddon.Addon().getLocalizedString
setSetting          = xbmcaddon.Addon().setSetting
getSetting          = xbmcaddon.Addon().getSetting
addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")
addonFullId         = addonName + addonVersion
addonDesc           = language(30450).encode("utf-8")
cache               = StorageServer.StorageServer(addonFullId,1).cacheFunction
cache2              = StorageServer.StorageServer(addonFullId,24).cacheFunction
cache3              = StorageServer.StorageServer(addonFullId,720).cacheFunction
addonIcon           = os.path.join(addonPath,'icon.png')
addonFanart         = os.path.join(addonPath,'fanart.jpg')
addonArt            = os.path.join(addonPath,'resources/art')
addonDownloads      = os.path.join(addonPath,'resources/art/Downloads.png')
addonPages          = os.path.join(addonPath,'resources/art/Pages.png')
addonGenres         = os.path.join(addonPath,'resources/art/Genres.png')
addonYears          = os.path.join(addonPath,'resources/art/Years.png')
addonLanguages      = os.path.join(addonPath,'resources/art/Languages.png')
addonNext           = os.path.join(addonPath,'resources/art/Next.png')
dataPath            = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
viewData            = os.path.join(dataPath,'views.cfg')
offData             = os.path.join(dataPath,'offset.cfg')
favData             = os.path.join(dataPath,'favourites.cfg')


class main:
    def __init__(self):
        global action
        index().container_data()
        params = {}
        splitparams = sys.argv[2][sys.argv[2].find('?') + 1:].split('&')
        for param in splitparams:
            if (len(param) > 0):
                splitparam = param.split('=')
                key = splitparam[0]
                try:    value = splitparam[1].encode("utf-8")
                except: value = splitparam[1]
                params[key] = value

        try:        action = urllib.unquote_plus(params["action"])
        except:     action = None
        try:        name = urllib.unquote_plus(params["name"])
        except:     name = None
        try:        url = urllib.unquote_plus(params["url"])
        except:     url = None
        try:        image = urllib.unquote_plus(params["image"])
        except:     image = None
        try:        query = urllib.unquote_plus(params["query"])
        except:     query = None
        try:        title = urllib.unquote_plus(params["title"])
        except:     title = None
        try:        year = urllib.unquote_plus(params["year"])
        except:     year = None
        try:        imdb = urllib.unquote_plus(params["imdb"])
        except:     imdb = None

        if action == None:                          root().get()
        elif action == 'item_play':                 contextMenu().item_play()
        elif action == 'item_random_play':          contextMenu().item_random_play()
        elif action == 'item_queue':                contextMenu().item_queue()
        elif action == 'favourite_add':             contextMenu().favourite_add(favData, name, url, image, imdb)
        elif action == 'favourite_from_search':     contextMenu().favourite_from_search(favData, name, url, image, imdb)
        elif action == 'favourite_delete':          contextMenu().favourite_delete(favData, name, url)
        elif action == 'favourite_moveUp':          contextMenu().favourite_moveUp(favData, name, url)
        elif action == 'favourite_moveDown':        contextMenu().favourite_moveDown(favData, name, url)
        elif action == 'playlist_open':             contextMenu().playlist_open()
        elif action == 'settings_open':             contextMenu().settings_open()
        elif action == 'addon_home':                contextMenu().addon_home()
        elif action == 'view_movies':               contextMenu().view('movies')
        elif action == 'metadata_movies':           contextMenu().metadata('movie', name, url, imdb, '', '')
        elif action == 'metadata_movies2':          contextMenu().metadata2('movie', name, url, imdb, '', '')
        elif action == 'playcount_movies':          contextMenu().playcount('movie', imdb, '', '')
        elif action == 'library':                   contextMenu().library(name, url)
        elif action == 'download':                  contextMenu().download(name, url)
        elif action == 'trailer':                   contextMenu().trailer(name, url)
        elif action == 'movies':                    movies().get(url)
        elif action == 'movies_search':             movies().viooz_search(query)
        elif action == 'movies_favourites':         favourites().movies()
        elif action == 'play':                      resolver().run(url, name)

        if action is None:
            pass
        elif action.startswith('movies'):
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            index().container_view('movies', {'skin.confluence' : 500})
        xbmcplugin.setPluginFanart(int(sys.argv[1]), addonFanart)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return

class getUrl(object):
    def __init__(self, url, close=True, proxy=None, post=None, mobile=False, referer=None, cookie=None, output='', timeout='10'):
        if not proxy is None:
            proxy_handler = urllib2.ProxyHandler({'http':'%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if output == 'cookie' or not close == True:
            import cookielib
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post is None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url,None)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
        if not referer is None:
            request.add_header('Referer', referer)
        if not cookie is None:
            request.add_header('cookie', cookie)
        response = urllib2.urlopen(request, timeout=int(timeout))
        if output == 'cookie':
            result = str(response.headers.get('Set-Cookie'))
        elif output == 'geturl':
            result = response.geturl()
        else:
            result = response.read()
        if close == True:
            response.close()
        self.result = result

class uniqueList(object):
    def __init__(self, list):
        uniqueSet = set()
        uniqueList = []
        for n in list:
            if n not in uniqueSet:
                uniqueSet.add(n)
                uniqueList.append(n)
        self.list = uniqueList

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)

class player(xbmc.Player):
    def __init__ (self):
        self.property = addonName+'player_status'
        xbmc.Player.__init__(self)

    def run(self, name, url, imdb='0'):
        self.video_info(name, imdb)

        if xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        else:
            try:
                file = self.name + '.strm'
                file = file.translate(None, '\/:*?"<>|')

                meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["title", "genre", "year", "rating", "director", "trailer", "tagline", "plot", "plotoutline", "originaltitle", "lastplayed", "playcount", "writer", "studio", "mpaa", "country", "imdbnumber", "runtime", "votes", "fanart", "thumbnail", "file", "sorttitle", "resume", "dateadded"]}, "id": 1}' % (self.year, str(int(self.year)+1), str(int(self.year)-1)))
                meta = unicode(meta, 'utf-8', errors='ignore')
                meta = json.loads(meta)
                meta = meta['result']['movies']
                self.meta = [i for i in meta if i['file'].endswith(file)][0]
                meta = {'title': self.meta['title'], 'originaltitle': self.meta['originaltitle'], 'year': self.meta['year'], 'genre': str(self.meta['genre']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'director': str(self.meta['director']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'country': str(self.meta['country']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'rating': self.meta['rating'], 'votes': self.meta['votes'], 'mpaa': self.meta['mpaa'], 'duration': self.meta['runtime'], 'trailer': self.meta['trailer'], 'writer': str(self.meta['writer']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'studio': str(self.meta['studio']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'tagline': self.meta['tagline'], 'plotoutline': self.meta['plotoutline'], 'plot': self.meta['plot']}
                poster = self.meta['thumbnail']
            except:
                meta = {'label' : self.name, 'title' : self.name}
                poster = ''
            item = xbmcgui.ListItem(path=url, iconImage="DefaultVideo.png", thumbnailImage=poster)
            item.setInfo( type="Video", infoLabels= meta )
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        for i in range(1, 21):
            try: self.totalTime = self.getTotalTime()
            except: self.totalTime = 0
            if not self.totalTime == 0: continue
            xbmc.sleep(1000)
        if self.totalTime == 0: return

        while True:
            try: self.currentTime = self.getTime()
            except: break
            xbmc.sleep(1000)

    def video_info(self, name, imdb):
        self.name = name
        self.content = 'movie'
        self.title = self.name.rsplit(' (', 1)[0].strip()
        self.year = '%04d' % int(self.name.rsplit(' (', 1)[-1].split(')')[0])
        if imdb == '0': imdb = metaget.get_meta('movie', self.title ,year=str(self.year))['imdb_id']
        self.imdb = re.sub('[^0-9]', '', imdb)
        return

    def offset_add(self):
        try:
            file = open(offData, 'a+')
            file.write('"%s"|"%s"|"%s"\n' % (self.name, self.imdb, self.currentTime))
            file.close()
        except:
            return

    def offset_delete(self):
        try:
            file = xbmcvfs.File(offData)
            read = file.read()
            file.close()
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"|"%s"' % (self.name, self.imdb) in x][0]
            list = re.compile('(".+?\n)').findall(read.replace(line, ''))
            file = open(offData, 'w')
            for line in list: file.write(line)
            file.close()
        except:
            return

    def offset_read(self):
        try:
            self.offset = '0'
            file = xbmcvfs.File(offData)
            read = file.read()
            file.close()
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"|"%s"' % (self.name, self.imdb) in x][0]
            self.offset = re.compile('".+?"[|]".+?"[|]"(.+?)"').findall(line)[0]
        except:
            return

    def change_watched(self):
        try:
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.meta['movieid']))
        except:
            metaget.change_watched(self.content, '', self.imdb, season='', episode='', year='', watched=7)

    def resume_playback(self):
        offset = float(self.offset)
        if not offset > 0: return
        minutes, seconds = divmod(offset, 60)
        hours, minutes = divmod(minutes, 60)
        offset_time = '%02d:%02d:%02d' % (hours, minutes, seconds)
        yes = index().yesnoDialog('%s %s' % (language(30353).encode("utf-8"), offset_time), '', self.name, language(30354).encode("utf-8"), language(30355).encode("utf-8"))
        if yes: self.seekTime(offset)

    def status(self):
        getProperty = index().getProperty(self.property)
        index().clearProperty(self.property)
        if not xbmc.getInfoLabel('Container.FolderPath') == '': return
        if getProperty == 'true': return True
        return

    def onPlayBackStarted(self):
        if getSetting("resume_playback") == 'true':
            self.offset_read()
            self.resume_playback()

        subtitles().get(self.name)

    def onPlayBackEnded(self):
        if xbmc.getInfoLabel('Container.FolderPath') == '': index().setProperty(self.property, 'true')
        self.change_watched()
        self.offset_delete()
        index().container_refresh()

    def onPlayBackStopped(self):
        index().clearProperty(self.property)
        if self.currentTime / self.totalTime >= .9:
            self.change_watched()
        self.offset_delete()
        self.offset_add()
        index().container_refresh()

class subtitles:
    def get(self, name):
        subs = getSetting("subs")
        if subs == '1': self.greek(name)

    def greek(self, name):
        try:
            import shutil, zipfile, time
            sub_tmp = os.path.join(dataPath,'sub_tmp')
            sub_tmp2 = os.path.join(sub_tmp, "subs")
            sub_stream = os.path.join(dataPath,'sub_stream')
            sub_file = os.path.join(sub_tmp, 'sub_tmp.zip')
            try: os.makedirs(dataPath)
            except: pass
            try: os.remove(sub_tmp)
            except: pass
            try: shutil.rmtree(sub_tmp)
            except: pass
            try: os.makedirs(sub_tmp)
            except: pass
            try: os.remove(sub_stream)
            except: pass
            try: shutil.rmtree(sub_stream)
            except: pass
            try: os.makedirs(sub_stream)
            except: pass

            subtitles = []
            query = ''.join(e for e in name if e.isalnum() or e == ' ')
            query = urllib.quote_plus(query)
            url = 'http://www.greeksubtitles.info/search.php?name=' + query
            result = getUrl(url).result
            result = result.decode('iso-8859-7').encode('utf-8')
            result = result.lower().replace('"',"'")
            match = "get_greek_subtitles[.]php[?]id=(.+?)'.+?%s.+?<"
            quality = ['bluray', 'brrip', 'bdrip', 'dvdrip', 'hdtv']
            for q in quality:
                subtitles += re.compile(match % q).findall(result)
            if subtitles == []: raise Exception()
            for subtitle in subtitles:
                url = 'http://www.findsubtitles.eu/getp.php?id=' + subtitle
                response = urllib.urlopen(url)
                content = response.read()
                response.close()
                if content[:4] == 'PK': break

            file = open(sub_file, 'wb')
            file.write(content)
            file.close()
            file = zipfile.ZipFile(sub_file, 'r')
            file.extractall(sub_tmp)
            file.close()
            files = os.listdir(sub_tmp2)
            if files == []: raise Exception()
            file = [i for i in files if i.endswith('.srt') or i.endswith('.sub')]
            if file == []:
                pack = [i for i in files if i.endswith('.zip') or i.endswith('.rar')]
                pack = os.path.join(sub_tmp2, pack[0])
                xbmc.executebuiltin('Extract("%s","%s")' % (pack, sub_tmp2))
                time.sleep(1)
            files = os.listdir(sub_tmp2)
            file = [i for i in files if i.endswith('.srt') or i.endswith('.sub')][0]
            copy = os.path.join(sub_tmp2, file)
            shutil.copy(copy, sub_stream)
            try: shutil.rmtree(sub_tmp)
            except: pass
            file = os.path.join(sub_stream, file)
            if not os.path.isfile(file): raise Exception()

            xbmc.Player().setSubtitles(file)
        except:
            try: shutil.rmtree(sub_tmp)
            except: pass
            try: shutil.rmtree(sub_stream)
            except: pass
            index().infoDialog(language(30317).encode("utf-8"), name)
            return

class index:
    def infoDialog(self, str, header=addonName):
        try: xbmcgui.Dialog().notification(header, str, addonIcon, 3000, sound=False)
        except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonIcon))

    def okDialog(self, str1, str2, header=addonName):
        xbmcgui.Dialog().ok(header, str1, str2)

    def selectDialog(self, list, header=addonName):
        select = xbmcgui.Dialog().select(header, list)
        return select

    def yesnoDialog(self, str1, str2, header=addonName, str3='', str4=''):
        answer = xbmcgui.Dialog().yesno(header, str1, str2, '', str4, str3)
        return answer

    def getProperty(self, str):
        property = xbmcgui.Window(10000).getProperty(str)
        return property

    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)

    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)

    def addon_status(self, id):
        check = xbmcaddon.Addon(id=id).getAddonInfo("name")
        if not check == addonName: return True

    def container_refresh(self):
        xbmc.executebuiltin("Container.Refresh")

    def container_data(self):
        if not xbmcvfs.exists(dataPath):
            xbmcvfs.mkdir(dataPath)
        if not xbmcvfs.exists(favData):
            file = xbmcvfs.File(favData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(viewData):
            file = xbmcvfs.File(viewData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(offData):
            file = xbmcvfs.File(offData, 'w')
            file.write('')
            file.close()

    def container_view(self, content, viewDict):
        try:
            skin = xbmc.getSkinDir()
            file = xbmcvfs.File(viewData)
            read = file.read().replace('\n','')
            file.close()
            view = re.compile('"%s"[|]"%s"[|]"(.+?)"' % (skin, content)).findall(read)[0]
            xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
        except:
            try:
                id = str(viewDict[skin])
                xbmc.executebuiltin('Container.SetViewMode(%s)' % id)
            except:
                pass

    def rootList(self, rootList):
        total = len(rootList)
        for i in rootList:
            try:
                name = language(i['name']).encode("utf-8")
                image = '%s/%s' % (addonArt, i['image'])
                action = i['action']
                u = '%s?action=%s' % (sys.argv[0], action)

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems([], replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def pageList(self, pageList):
        if pageList == None: return

        total = len(pageList)
        for i in pageList:
            try:
                name, url, image = i['name'], i['url'], i['image']
                sysname, sysurl, sysimage = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image)

                u = '%s?action=movies&url=%s' % (sys.argv[0], sysurl)

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems([], replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def nextList(self, nextList):
        try: next = nextList[0]['next']
        except: return
        if next == '': return
        name, url, image = language(30361).encode("utf-8"), next, addonNext
        sysurl = urllib.quote_plus(url)

        u = '%s?action=movies&url=%s' % (sys.argv[0], sysurl)

        item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
        item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
        item.setProperty("Fanart_Image", addonFanart)
        item.addContextMenuItems([], replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)

    def downloadList(self):
        u = getSetting("downloads")
        if u == '': return
        name, image = language(30363).encode("utf-8"), addonDownloads

        item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
        item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
        item.setProperty("Fanart_Image", addonFanart)
        item.addContextMenuItems([], replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)

    def movieList(self, movieList):
        if movieList == None: return

        file = xbmcvfs.File(favData)
        favRead = file.read()
        file.close()

        total = len(movieList)
        for i in movieList:
            try:
                name, url, image, title, year, imdb, genre, plot = i['name'], i['url'], i['image'], i['title'], i['year'], i['imdb'], i['genre'], i['plot']
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '

                sysname, sysurl, sysimage, systitle, sysimdb = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(title), urllib.quote_plus(imdb)
                u = '%s?action=play&name=%s&url=%s&t=%s' % (sys.argv[0], sysname, sysurl, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))

                if getSetting("meta") == 'true':
                    meta = metaget.get_meta('movie', title ,year=year)
                    playcountMenu = language(30407).encode("utf-8")
                    if meta['overlay'] == 6: playcountMenu = language(30408).encode("utf-8")
                    metaimdb = urllib.quote_plus(re.sub('[^0-9]', '', meta['imdb_id']))
                    trailer, poster = urllib.quote_plus(meta['trailer_url']), meta['cover_url']
                    if trailer == '': trailer = sysurl
                    if poster == '': poster = image
                else:
                    meta = {'label': title, 'title': title, 'year': year, 'imdb_id' : imdb, 'genre' : genre, 'plot': plot}
                    trailer, poster = sysurl, image
                if getSetting("meta") == 'true' and getSetting("fanart") == 'true':
                    fanart = meta['backdrop_url']
                    if fanart == '': fanart = addonFanart
                else:
                    fanart = addonFanart

                cm = []
                cm.append((language(30405).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30406).encode("utf-8"), 'RunPlugin(%s?action=download&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                cm.append((language(30412).encode("utf-8"), 'Action(Info)'))
                if action == 'movies_favourites':
                    if not getSetting("fav_sort") == '2': cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_movies&name=%s&url=%s&imdb=%s)' % (sys.argv[0], systitle, sysurl, metaimdb)))
                    if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_movies&imdb=%s)' % (sys.argv[0], metaimdb)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    if getSetting("fav_sort") == '2': cm.append((language(30419).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveUp&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    if getSetting("fav_sort") == '2': cm.append((language(30420).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveDown&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30421).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                elif action == 'movies_search':
                    cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_from_search&name=%s&imdb=%s&url=%s&image=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                    cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))
                else:
                    cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_movies2&name=%s&url=%s&imdb=%s)' % (sys.argv[0], systitle, sysurl, metaimdb)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    if not '"%s"' % url in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&name=%s&imdb=%s&url=%s&image=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=poster)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("art(poster)", poster)
                item.setProperty("Fanart_Image", fanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=False)
            except:
                pass

class contextMenu:
    def item_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.unshuffle()
        xbmc.Player().play(playlist)

    def item_random_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.shuffle()
        xbmc.Player().play(playlist)

    def item_queue(self):
        xbmc.executebuiltin('Action(Queue)')

    def playlist_open(self):
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')

    def settings_open(self):
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % (addonId))

    def addon_home(self):
        xbmc.executebuiltin('Container.Update(plugin://%s/,replace)' % (addonId))

    def view(self, content):
        try:
            skin = xbmc.getSkinDir()
            skinPath = xbmc.translatePath('special://skin/')
            xml = os.path.join(skinPath,'addon.xml')
            file = xbmcvfs.File(xml)
            read = file.read().replace('\n','')
            file.close()
            try: src = re.compile('defaultresolution="(.+?)"').findall(read)[0]
            except: src = re.compile('<res.+?folder="(.+?)"').findall(read)[0]
            src = os.path.join(skinPath, src)
            src = os.path.join(src, 'MyVideoNav.xml')
            file = xbmcvfs.File(src)
            read = file.read().replace('\n','')
            file.close()
            views = re.compile('<views>(.+?)</views>').findall(read)[0]
            views = [int(x) for x in views.split(',')]
            for view in views:
                label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
                if not (label == '' or label is None): break
            file = xbmcvfs.File(viewData)
            read = file.read()
            file.close()
            file = open(viewData, 'w')
            for line in re.compile('(".+?\n)').findall(read):
                if not line.startswith('"%s"|"%s"|"' % (skin, content)): file.write(line)
            file.write('"%s"|"%s"|"%s"\n' % (skin, content, str(view)))
            file.close()
            viewName = xbmc.getInfoLabel('Container.Viewmode')
            index().infoDialog('%s%s%s' % (language(30301).encode("utf-8"), viewName, language(30302).encode("utf-8")))
        except:
            return

    def favourite_add(self, data, name, url, image, imdb):
        try:
            index().container_refresh()
            file = open(data, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"\n' % (name, imdb, url, image))
            file.close()
            index().infoDialog(language(30303).encode("utf-8"), name)
        except:
            return

    def favourite_from_search(self, data, name, url, image, imdb):
        try:
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            if url in read:
                index().infoDialog(language(30307).encode("utf-8"), name)
                return
            file = open(data, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"\n' % (name, imdb, url, image))
            file.close()
            index().infoDialog(language(30303).encode("utf-8"), name)
        except:
            return

    def favourite_delete(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            list = re.compile('(".+?\n)').findall(read.replace(line, ''))
            file = open(data, 'w')
            for line in list: file.write(line)
            file.close()
            index().infoDialog(language(30304).encode("utf-8"), name)
        except:
            return

    def favourite_moveUp(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            list = re.compile('(".+?)\n').findall(read)
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            i = list.index(line)
            if i == 0 : return
            list[i], list[i-1] = list[i-1], list[i]
            file = open(data, 'w')
            for line in list: file.write('%s\n' % (line))
            file.close()
            index().infoDialog(language(30305).encode("utf-8"), name)
        except:
            return

    def favourite_moveDown(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            list = re.compile('(".+?)\n').findall(read)
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            i = list.index(line)
            if i+1 == len(list): return
            list[i], list[i+1] = list[i+1], list[i]
            file = open(data, 'w')
            for line in list: file.write('%s\n' % (line))
            file.close()
            index().infoDialog(language(30306).encode("utf-8"), name)
        except:
            return

    def metadata(self, content, name, url, imdb, season, episode):
        try:
            list = []
            if content == 'movie' or content == 'tvshow':
                if content == 'movie':
                    search = metaget.search_movies(name)
                elif content == 'tvshow':
                    search = []
                    result = metahandlers.TheTVDB().get_matching_shows(name)
                    for i in result: search.append({'tvdb_id': i[0], 'title': i[1], 'imdb_id': i[2]})
                for i in search:
                    label = i['title']
                    if 'year' in i: label += ' (%s)' % i['year']
                    list.append(label)
                select = index().selectDialog(list, language(30364).encode("utf-8"))
                if select > -1:
                    if content == 'movie':
                        new_imdb = metaget.get_meta('movie', search[select]['title'] ,year=search[select]['year'])['imdb_id']
                    elif content == 'tvshow':
                        new_imdb = search[select]['imdb_id']
                    new_imdb = re.sub('[^0-9]', '', new_imdb)
                    sources = []
                    try: sources.append(favData)
                    except: pass
                    try: sources.append(favData2)
                    except: pass
                    try: sources.append(subData)
                    except: pass
                    if sources == []: raise Exception()
                    for source in sources:
                        try:
                            file = xbmcvfs.File(source)
                            read = file.read()
                            file.close()
                            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
                            line2 = line.replace('"0"', '"%s"' % new_imdb).replace('"%s"' % imdb, '"%s"' % new_imdb)
                            file = open(source, 'w')
                            file.write(read.replace(line, line2))
                            file.close()
                        except:
                            pass
                    metaget.update_meta(content, '', imdb, year='')
                    index().container_refresh()
            elif content == 'season':
                metaget.update_episode_meta('', imdb, season, episode)
                index().container_refresh()
            elif content == 'episode':
                metaget.update_season('', imdb, season)
                index().container_refresh()
        except:
            return

    def metadata2(self, content, name, url, imdb, season, episode):
        try:
            if content == 'movie' or content == 'tvshow':
                metaget.update_meta(content, '', imdb, year='')
                index().container_refresh()
            elif content == 'season':
                metaget.update_episode_meta('', imdb, season, episode)
                index().container_refresh()
            elif content == 'episode':
                metaget.update_season('', imdb, season)
                index().container_refresh()
        except:
            return

    def playcount(self, content, imdb, season, episode):
        try:
            metaget.change_watched(content, '', imdb, season=season, episode=episode, year='', watched='')
            index().container_refresh()
        except:
            return

    def library(self, name, url, silent=False):
        try:
            library = xbmc.translatePath(getSetting("movie_library"))
            sysname, sysurl = urllib.quote_plus(name), urllib.quote_plus(url)
            content = '%s?action=play&name=%s&url=%s' % (sys.argv[0], sysname, sysurl)
            enc_name = name.translate(None, '\/:*?"<>|')
            folder = os.path.join(library, enc_name)
            stream = os.path.join(folder, enc_name + '.strm')
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(library)
            xbmcvfs.mkdir(folder)
            file = xbmcvfs.File(stream, 'w')
            file.write(content)
            file.close()
            if silent == False:
                index().infoDialog(language(30311).encode("utf-8"), name)
        except:
            return

    def download(self, name, url):
        try:
            property = (addonName+name)+'download'
            download = xbmc.translatePath(getSetting("downloads"))
            enc_name = name.translate(None, '\/:*?"<>|')
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(download)

            file = [i for i in xbmcvfs.listdir(download)[1] if i.startswith(enc_name + '.')]
            if not file == []: file = os.path.join(download, file[0])
            else: file = None

            if download == '':
            	yes = index().yesnoDialog(language(30341).encode("utf-8"), language(30342).encode("utf-8"))
            	if yes: contextMenu().settings_open()
            	return

            if file is None:
            	pass
            elif not file.endswith('.tmp'):
            	yes = index().yesnoDialog(language(30343).encode("utf-8"), language(30344).encode("utf-8"), name)
            	if yes:
            	    xbmcvfs.delete(file)
            	else:
            	    return
            elif file.endswith('.tmp'):
            	if index().getProperty(property) == 'open':
            	    yes = index().yesnoDialog(language(30345).encode("utf-8"), language(30346).encode("utf-8"), name)
            	    if yes: index().setProperty(property, 'cancel')
            	    return
            	else:
            	    xbmcvfs.delete(file)

            url = resolver().run(url, name, download=True)
            if url is None: return
            ext = url.rsplit('/', 1)[-1].rsplit('?', 1)[0].rsplit('|', 1)[0].strip().lower()
            ext = os.path.splitext(ext)[1][1:]
            if ext == '': ext = 'mp4'
            stream = os.path.join(download, enc_name + '.' + ext)
            temp = stream + '.tmp'

            count = 0
            CHUNK = 16 * 1024
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
            request.add_header('Cookie', 'video=true') #add cookie
            response = urllib2.urlopen(request, timeout=10)
            size = response.info()["Content-Length"]

            file = xbmcvfs.File(temp, 'w')
            index().setProperty(property, 'open')
            index().infoDialog(language(30308).encode("utf-8"), name)
            while True:
            	chunk = response.read(CHUNK)
            	if not chunk: break
            	if index().getProperty(property) == 'cancel': raise Exception()
            	if xbmc.abortRequested == True: raise Exception()
            	part = xbmcvfs.File(temp)
            	quota = int(100 * float(part.size())/float(size))
            	part.close()
            	if not count == quota and count in [0,10,20,30,40,50,60,70,80,90]:
            		index().infoDialog(language(30309).encode("utf-8") + str(count) + '%', name)
            	file.write(chunk)
            	count = quota
            response.close()
            file.close()

            index().clearProperty(property)
            xbmcvfs.rename(temp, stream)
            index().infoDialog(language(30310).encode("utf-8"), name)
        except:
            file.close()
            index().clearProperty(property)
            xbmcvfs.delete(temp)
            sys.exit()
            return

    def trailer(self, name, url):
        url = trailer().run(name, url)
        if url is None: return
        item = xbmcgui.ListItem(path=url)
        item.setProperty("IsPlayable", "true")
        xbmc.Player().play(url, item)

class favourites:
    def __init__(self):
        self.list = []

    def movies(self):
        file = xbmcvfs.File(favData)
        read = file.read()
        file.close()

        match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
        for name, imdb, url, image in match:
            try: year = re.compile('[(](\d{4})[)]').findall(name)[-1]
            except: year = '0'
            title = name.replace('(%s)' % year, '').strip()
            self.list.append({'name': name, 'url': url, 'image': image, 'title': title, 'year': year, 'imdb': imdb, 'genre': '', 'plot': ''})

        if getSetting("fav_sort") == '0':
            self.list = sorted(self.list, key=itemgetter('title'))
        elif getSetting("fav_sort") == '1':
            self.list = sorted(self.list, key=itemgetter('title'))[::-1]
            self.list = sorted(self.list, key=itemgetter('year'))[::-1]

        index().movieList(self.list)

class root:
    def get(self):
        rootList = []
        '''
        rootList.append({'name': 30501, 'image': 'Title.png', 'action': 'movies_title'})
        rootList.append({'name': 30502, 'image': 'IMDb.png', 'action': 'movies_imdb'})
        rootList.append({'name': 30503, 'image': 'Release.png', 'action': 'movies_release'})
        rootList.append({'name': 30504, 'image': 'Added.png', 'action': 'movies_added'})
        rootList.append({'name': 30505, 'image': 'Rating.png', 'action': 'movies_rating'})
        rootList.append({'name': 30506, 'image': 'Views.png', 'action': 'movies_views'})
        rootList.append({'name': 30507, 'image': 'Pages.png', 'action': 'pages_movies'})
        rootList.append({'name': 30508, 'image': 'Genres.png', 'action': 'genres_movies'})
        rootList.append({'name': 30509, 'image': 'Years.png', 'action': 'years_movies'})
        rootList.append({'name': 30510, 'image': 'Languages.png', 'action': 'languages_movies'})
        '''
        rootList.append({'name': 30511, 'image': 'Favourites.png', 'action': 'movies_favourites'})
        rootList.append({'name': 30512, 'image': 'Search.png', 'action': 'movies_search'})
        index().rootList(rootList)
        index().downloadList()

class proxy:
    def __init__(self):
        self.server = None
        if getSetting("proxy") == 'true' and not (getSetting("proxy_ip") == '' or getSetting("proxy_port") == ''):
            self.server = '%s:%s' % (getSetting("proxy_ip"), getSetting("proxy_port"))

class link:
    def __init__(self):
        self.viooz_base = 'http://viooz.co'
        self.viooz_static = 'http://static.viooz.co'
        self.viooz_search = 'http://viooz.co/search?s=t&q=%s'

class movies:
    def __init__(self):
        self.list = []
        self.data = []

    def viooz_search(self, query=None):
        if query is None:
            self.query = common.getUserInput(language(30362).encode("utf-8"), '')
        else:
            self.query = query
        if not (self.query is None or self.query == ''):
            self.query = link().viooz_search % urllib.quote_plus(self.query)
            self.list = self.viooz_list(self.query)
            index().movieList(self.list)

    def viooz_list(self, url):
        try:
            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            movies = result.split('class="infos"')
        except:
            return

        for movie in movies:
            try:
                name = common.parseDOM(movie, "a", ret="title")[0]
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                match = re.findall('(.+?)[(](\d{4})[)]', name)[0]

                title = match[0].strip()
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = match[-1].strip()
                year = re.sub('[^0-9]', '', year)
                year = year.encode('utf-8')

                url = common.parseDOM(movie, "a", ret="href")[0]
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = common.parseDOM(movie, "img", ret="src")
                image = [i for i in image if i.startswith(link().viooz_static)][-1]
                image = common.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                try:
                    plot = common.parseDOM(movie, "div", attrs = { "class": "summary" })[0]
                    plot = common.replaceHTMLCodes(plot)
                    plot = plot.encode('utf-8')
                except:
                    plot = ''

                self.list.append({'name': name, 'url': url, 'image': image, 'title': title, 'year': year, 'imdb': '0', 'genre': '', 'plot': plot, 'next': ''})
            except:
                pass

        return self.list

class trailer:
    def __init__(self):
        self.youtube_base = 'http://www.youtube.com'
        self.youtube_query = 'http://gdata.youtube.com/feeds/api/videos?q='
        self.youtube_watch = 'http://www.youtube.com/watch?v=%s'
        self.youtube_info = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2'

    def run(self, name, url):
        try:
            if url.startswith(self.youtube_base):
                url = self.youtube(url)
                if url is None: raise Exception()
                return url
            elif not url.startswith('http://'):
                url = self.youtube_watch % url
                url = self.youtube(url)
                if url is None: raise Exception()
                return url
            else:
                raise Exception()
        except:
            url = self.youtube_query + name + ' trailer'
            url = self.youtube_search(url)
            if url is None: return
            return url

    def youtube_search(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30321).encode("utf-8"), language(30322).encode("utf-8"))
                return

            query = url.split("?q=")[-1].split("/")[-1].split("?")[0]
            url = url.replace(query, urllib.quote_plus(query))
            result = getUrl(url).result
            result = common.parseDOM(result, "entry")
            result = common.parseDOM(result, "id")

            for url in result[:5]:
                url = url.split("/")[-1]
                url = self.youtube_watch % url
                url = self.youtube(url)
                if not url is None: return url
        except:
            return

    def youtube(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30321).encode("utf-8"), language(30322).encode("utf-8"))
                return
            id = url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]
            state, reason = None, None
            result = getUrl(self.youtube_info % id).result
            try:
                state = common.parseDOM(result, "yt:state", ret="name")[0]
                reason = common.parseDOM(result, "yt:state", ret="reasonCode")[0]
            except:
                pass
            if state == 'deleted' or state == 'rejected' or state == 'failed' or reason == 'requesterRegion' : return
            try:
                result = getUrl(self.youtube_watch % id).result
                alert = common.parseDOM(result, "div", attrs = { "id": "watch7-notification-area" })[0]
                return
            except:
                pass
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return url
        except:
            return

class resolver:
    def run(self, url, name, download=False):
        try:
            if player().status() is True: return
            url = self.viooz(url)
            if url is None: raise Exception()

            if download == True: return url
            player().run(name, url)
            return url
        except:
            index().infoDialog(language(30318).encode("utf-8"))
            return

    def viooz(self, url):
        try:
            import decrypter
            result = getUrl(url).result

            url = re.compile('proxy[.]link=viooz[*](.+?)&').findall(result)[0]
            url = common.replaceHTMLCodes(url)
            url = decrypter.decrypter(198,128).decrypt(url,'aXV7OaSC804VayTCIOba','ECB').split('\0')[0]

            result = getUrl(url).result
            url = common.parseDOM(result, "link", ret="href", attrs = { "rel": "alternate" })[0]
            url = common.replaceHTMLCodes(url)

            result = getUrl(url).result
            url = common.parseDOM(result, "media:content", ret="url")
            url = [i for i in url if 'videoplayback?' in i][-1]
            url = common.replaceHTMLCodes(url)

            url = url.replace('http://', 'https://')
            url = getUrl(url, output='geturl').result
            return url
        except:
            return


main()