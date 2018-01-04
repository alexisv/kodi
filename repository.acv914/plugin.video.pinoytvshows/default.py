import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import re
import urllib2
import urllib
import math

BASE_URL = "https://www.pinoytvshows.me"
 
from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer

def getHTML(url):
        try:
            print 'getHTML :: url = ' + url
            req = urllib2.build_opener()
            req.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')]
            #req = urllib2.Request(url)
            #response = urllib2.urlopen(req)
            response = req.open(url)
            link = response.read()
            response.close()
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
        else:
            return link

def listPage(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(html) 
    # Items
    #tab1 = soup.find('div', attrs={'id': 'tabs-1'})
    #headings = tab1.findAll('h3')
    #iframes = tab1.findAll('iframe')
    thumbnail_meta = soup.find('meta', attrs={'property': 'og:image'})
    try:
        thumbnail = thumbnail_meta['content']
    except:
        thumbnail = "DefaultFolder.png"
    title_tag = soup.find('title')
    try:
        title = title_tag.contents[0]
    except:
        title = "no title"
    #notify(thumbnail)
    iframes = soup.findAll('iframe')
    hcnt = 0
    for iframe in iframes:
        partcnt = hcnt + 1
        ititle = "Part " + str(partcnt)
        lurl = iframe['src']
        url = get_vidlink(lurl)
        thumb = thumbnail
        plot = ititle + ' of ' + title
        #time = "time"
        listitem=xbmcgui.ListItem(ititle, iconImage=thumb, thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot })
        listitem.setPath(url)
        listitem.setProperty("IsPlayable", "true")
        listitem.setProperty("fanart_image", thumb)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
        hcnt = hcnt + 1        
    return

def get_vidlink(url):
    vidlink = ''
    match_pinoytvshows = re.compile('www.pinoytvshows.me').findall(url)
    match_linksharetv = re.compile('http://www.linkshare.tv/mp4/\?url').findall(url)
    match_dailymotion = re.compile('www.dailymotion.com').findall(url)
    match_videorss = re.compile('http://videorss.net/mp4/\?url').findall(url)
    match_youtube = re.compile('www.youtube.com').findall(url)
    if match_pinoytvshows:
        vidlink = get_vidlink_pinoytvshows(url)
        match_youtube_in = re.compile('www.youtube.com').findall(vidlink)
        if match_youtube_in:
            vidlink = get_vidlink_youtube(vidlink)
    if match_linksharetv:
        vidlink = get_vidlink_linksharetv(url)
    if match_dailymotion:
        vidlink = get_vidlink_dailymotion(url)
    if match_videorss:
        vidlink = get_vidlink_linksharetv(url)
    if match_youtube:
        vidlink = get_vidlink_youtube(url)
    return vidlink

def get_vidlink_pinoytvshows(url):
    html = getHTML(urllib.unquote_plus(url))
    match = re.compile('file: "(.+?)"', re.DOTALL).findall(html)
    vidlink = match[0]
    return vidlink
    
def get_vidlink_dailymotion(url):
    match=re.compile('http://www.dailymotion.com/embed/video/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/video/(.+?)&dk;').findall(url+"&dk;")
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/swf/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/embed/video/(.+?)$').findall(url)
    link = 'http://www.dailymotion.com/embed/video/'+str(match[0])
    #req = get_page(link)
    #req = req.encode("UTF-8")
    req = getHTML(urllib.unquote_plus(url))
    matchFullHD = re.compile('"stream_h264_hd1080_url":"(.+?)"', re.DOTALL).findall(req)
    matchHD = re.compile('"stream_h264_hd_url":"(.+?)"', re.DOTALL).findall(req)
    matchHQ = re.compile('"stream_h264_hq_url":"(.+?)"', re.DOTALL).findall(req)
    matchSD = re.compile('"stream_h264_url":"(.+?)"', re.DOTALL).findall(req)
    matchLD = re.compile('"stream_h264_ld_url":"(.+?)"', re.DOTALL).findall(req)
    maxVideoQuality = "1080p"
    if matchFullHD and maxVideoQuality == "1080p":
        vidlink = urllib.unquote_plus(matchFullHD[0]).replace("\\", "")
    elif matchHD and (maxVideoQuality == "720p" or maxVideoQuality == "1080p"):
        vidlink = urllib.unquote_plus(matchHD[0]).replace("\\", "")
    elif matchHQ:
        vidlink = urllib.unquote_plus(matchHQ[0]).replace("\\", "")
    elif matchSD:
        vidlink = urllib.unquote_plus(matchSD[0]).replace("\\", "")
    elif matchLD:
        vidlink = urllib.unquote_plus(matchLD[0]).replace("\\", "")
    return vidlink

def get_vidlink_youtube(url):
    vidlink = ""
    if (url.find("youtube") > -1) and (url.find("playlists") > -1):
        playlistid=re.compile('playlists/(.+?)\?v').findall(url)
        vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
    elif (url.find("youtube") > -1) and (url.find("list=") > -1):
        playlistid=re.compile('videoseries\?list=(.+?)&').findall(url+"&")
        if (len(playlistid) > 0):
            vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
        else:
            playlistid = re.compile('list=(.+?)$').findall(url)
            vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
    elif (url.find("youtube") > -1) and (url.find("/p/") > -1):
        playlistid=re.compile('/p/(.+?)\?').findall(url)
        vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
    elif (url.find("youtube") > -1) and (url.find("/embed/") > -1):
        playlistid=re.compile('/embed/(.+?)\?').findall(url+"?")
        vidlink=getYoutube(playlistid[0])
        if vidlink == "":
            vidlink="plugin://plugin.video.youtube/?action=play_video&videoid="+playlistid[0]
    elif (url.find("youtube") > -1):
        #match=re.compile('(youtu\.be\/|youtube-nocookie\.com\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(url)
        #if(len(match) == 0):
        #    match=re.compile('http://www.youtube.com/watch\?v=(.+?)&dk;').findall(url)
        #if(len(match) == 0):
        #    match=re.compile('http://www.youtube.com/watch\?v=(.+)').findall(url)
        #if(len(match) > 0):
        #    lastmatch = match[0][len(match[0])-1].replace('v/','')
            #lastmatch = match[0][len(match[0])-1]
        #vidlink=getYoutube(lastmatch[0])
        match=re.compile('https://www.youtube.com/watch\?v=(.+)').findall(url)
        #if(len(match) > 0):
            #lastmatch = match[0][len(match[0])-1].replace('v/','')
            #msg = match[0]
            #notify(msg)
        vidlink=getYoutube(match[0])
        #notify(vidlink)
        if vidlink == "":
            #vidlink="plugin://plugin.video.youtube/?action=play_video&videoid="+lastmatch[0]
            vidlink="plugin://plugin.video.youtube/?action=play_video&videoid="+match[0]
    return vidlink   

def getYoutube(code):
    yturl = 'http://www.youtube.com/watch?v='+code+'&fmt=18'
    link = getHTML(yturl)
    #link = link.encode("UTF-8")
                            
    if len(re.compile('shortlink" href="http://youtu.be/(.+?)"').findall(link)) == 0:
        if len(re.compile('\'VIDEO_ID\': "(.+?)"').findall(link)) == 0:
            yturl2 = 'http://www.youtube.com/get_video_info?video_id='+code+'&asv=3&el=detailpage&hl=en_US'
            link = getHTML(yturl2)
            link = link.encode("UTF-8")
                            
    flashvars = extractFlashVars(link)
    if len(flashvars) == 0:
        return ""

    links = {}

    for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
        url_desc_map = cgi.parse_qs(url_desc)
        if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
            continue

        key = int(url_desc_map[u"itag"][0])
        url = u""
        if url_desc_map.has_key(u"url"):
            url = urllib.unquote(url_desc_map[u"url"][0])
        elif url_desc_map.has_key(u"stream"):
            url = urllib.unquote(url_desc_map[u"stream"][0])

        if url_desc_map.has_key(u"sig"):
            url = url + u"&signature=" + url_desc_map[u"sig"][0]
        links[key] = url
    highResoVid=selectVideoQuality(links)
    return highResoVid

def selectVideoQuality(links):
    link = links.get
    video_url = ""
    fmt_value = {
                                5: "240p h263 flv container",
                                18: "360p h264 mp4 container | 270 for rtmpe?",
                                22: "720p h264 mp4 container",
                                26: "???",
                                33: "???",
                                34: "360p h264 flv container",
                                35: "480p h264 flv container",
                                37: "1080p h264 mp4 container",
                                38: "720p vp8 webm container",
                                43: "360p h264 flv container",
                                44: "480p vp8 webm container",
                                45: "720p vp8 webm container",
                                46: "520p vp8 webm stereo",
                                59: "480 for rtmpe",
                                78: "seems to be around 400 for rtmpe",
                                82: "360p h264 stereo",
                                83: "240p h264 stereo",
                                84: "720p h264 stereo",
                                85: "520p h264 stereo",
                                100: "360p vp8 webm stereo",
                                101: "480p vp8 webm stereo",
                                102: "720p vp8 webm stereo",
                                120: "hd720",
                                121: "hd1080"
    }
    hd_quality = 1

    # SD videos are default, but we go for the highest res
    if (link(35)):
        video_url = link(35)
    elif (link(59)):
        video_url = link(59)
    elif link(44):
        video_url = link(44)
    elif (link(78)):
        video_url = link(78)
    elif (link(34)):
        video_url = link(34)
    elif (link(43)):
        video_url = link(43)
    elif (link(26)):
        video_url = link(26)
    elif (link(18)):
        video_url = link(18)
    elif (link(33)):
        video_url = link(33)
    elif (link(5)):
        video_url = link(5)

    if hd_quality > 1:    # <-- 720p
        if (link(22)):
            video_url = link(22)
        elif (link(45)):
            video_url = link(45)
        elif link(120):
            video_url = link(120)
    if hd_quality > 2:
        if (link(37)):
            video_url = link(37)
        elif link(121):
            video_url = link(121)

    if link(38) and False:
        video_url = link(38)
    for fmt_key in links.iterkeys():

        if link(int(fmt_key)):
            text = repr(fmt_key) + " - "
            if fmt_key in fmt_value:
                text += fmt_value[fmt_key]
            else:
                text += "Unknown"

            if (link(int(fmt_key)) == video_url):
                text += "*"
            else:
                print "- Missing fmt_value: " + repr(fmt_key)
    video_url += " | " + 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    return video_url

def extractFlashVars(data):
    found = False
    flashvars = ""
    for line in data.split("\n"):
        index = line.find("ytplayer.config =")
        if index != -1:
            cfgline = line.find("url_encoded_fmt_stream_map")
            if cfgline != -1:
                found = True
                p1 = line.find("=", (index-3))
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break
    if found:
        data=data.split(";(function()",1)[0]
        try:
            data = json.loads(data)
        except:
            return ""
        flashvars = data["args"]
    return flashvars

def get_vidlink_linksharetv(url):
    urlmatch = re.search('(?<=\=).+', url)
    vidlink = urlmatch.group(0)
    return vidlink
    
def nextPage(params):
    get = params.get
    url = get("url")
    return listPage(url)

def firstPage(url):
    html = getHTML(urllib.unquote_plus(url))
    # https://bugs.launchpad.net/beautifulsoup/+bug/838022
    BeautifulSoup.NESTABLE_TAGS['td'] = ['tr', 'table']
    soup = BeautifulSoup(html)

    for article in soup.findAll('article','latestPost excerpt layout-1'):
        h2 = article.find('h2', 'title front-view-title')
        try:
            title = h2.find('a')['title']
        except:
            title = "No title"
        try:
            link = h2.find('a')['href']
        except:
            link = None
        try:
            div = article.find('div','featured-thumbnail')
            try:
                thumbnail = div.find('img')['data-layzr']
            except:
                thumbnail = "DefaultFolder.png"
        except:
            div = None
            thumbnail = "DefaultFolder.png"

        if title and link:
            if BASE_URL in link:
                addPosts(title, link, thumbnail, 0)

    # Items
    #for links in soup.findAll('h2','title front-view-title'):
    #    for line in links.findAll('a'):
    #        try:
    #            title = links.find('a').contents[0]
    #        except:
    #            title = "No title"
    #        try:
    #            link = links.find('a')['href']
    #        except:
    #            link = None
    #        if title and link:
    #            if BASE_URL in link:
    #                addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), 0)

    # Search
    #addPosts('Search..', '&search=True')
    #
    #
    # Mga bagong mga post
    #newerlinks = soup.find('a', 'blog-pager-newer-link')
    #try:
    #    title = newerlinks.contents[0]
    #except:
    #    title = "Mga Mas Bagong Post"
    #try:
    #    link = newerlinks.attrs[1][1]
    #except:
    #    link = None
    #if title and link:
    #    addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), 1)
    #
    # Mga lumang mga post
    olderlinks = soup.find('a', 'next page-numbers')
    title = "Next Page"
    try:
        link = olderlinks.attrs[1][1]
    except:
        link = None
    if title and link:
        addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), "DefaultFolder.png", 1)
    return

def addPosts(title, url, thumbnail, first):
    listitem=xbmcgui.ListItem(title, iconImage=thumbnail)
    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot" : title } )
    if first == 1:
        xurl = "%s?otherpage=True&url=" % sys.argv[0]
    else:
        xurl = "%s?next=True&url=" % sys.argv[0]
    xurl = xurl + url
    #listitem.setInfo(infoLabels={ "Title": title, "Plot" : title })
    listitem.setPath(xurl)
    listitem.setProperty("fanart_image", thumbnail)
    folder = True
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=folder)

def notify(msg):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')
    __icon__ = __addon__.getAddonInfo('icon')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, msg, 4000, __icon__))
    return 0
 
def search_site():
    encodedSearchString = search()
    if not encodedSearchString == "":
        url = 'http://www.pinkbike.com/video/search/?q=' + encodedSearchString
        listPage(url)
    else:
        firstPage(BASE_URL)
    return

def search():
    searchString = unikeyboard("", 'Search PinkBike.com')
    if searchString == "":
        xbmcgui.Dialog().ok('PinkBike.com','Missing text')
    elif searchString:
        dialogProgress = xbmcgui.DialogProgress()
        dialogProgress.create('PinkBike.com', 'Searching for: ' , searchString)
        #The XBMC onscreen keyboard outputs utf-8 and this need to be encoded to unicode
    encodedSearchString = urllib.quote_plus(searchString.decode("utf_8").encode("raw_unicode_escape"))
    return encodedSearchString

#From old undertexter.se plugin    
def unikeyboard(default, message):
    keyboard = xbmc.Keyboard(default, message)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return ""

#FROM plugin.video.youtube.beta  -- converts the request url passed on by xbmc to our plugin into a dict  
def getParameters(parameterString):
    commands = {}
    splitCommands = parameterString[parameterString.find('?')+1:].split('&')
    for command in splitCommands: 
        if (len(command) > 0):
            splitCommand = command.split('=')
            name = splitCommand[0]
            value = splitCommand[1]
            commands[name] = value
    return commands

if (__name__ == "__main__" ):
    if (not sys.argv[2]):
        firstPage(BASE_URL)
    else:
        params = getParameters(sys.argv[2])
        get = params.get
        if (get("search")):
            search_site()
        if (get("next")) and not (get("search")):
            nextPage(params)
        if (get("otherpage")):
            firstPage(get("url"))

xbmcplugin.endOfDirectory(int(sys.argv[1]))