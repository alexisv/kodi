import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import re
import urllib2
import urllib
import urlparse
import json
from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer
addon_handle = sys.argv[1]
args = urlparse.parse_qs(sys.argv[2][1:])
thebase = sys.argv[0]

# the sources
magtvnaph_url = 'http://www.magtvnaph.com'
pinoytvshows_url = 'https://www.pinoytvshows.me'
teleseryi_url = 'http://www.teleseryi.info'

def getHTML(url):
        try:
            print 'getHTML :: url = ' + url
            req = urllib2.build_opener()
            req.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')]
            response = req.open(url)
            link = response.read()
            response.close()
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
            notify("HTTP error: %d" % e.code)
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
            notify("Network error: %s" % e.reason.args[1])
        else:
            return link

def firstPage():
    addPosts(str("Mag TV na"), magtvnaph_url, "DefaultFolder.png", 1)
    addPosts(str("Pinoy TV Shows"), pinoytvshows_url, "DefaultFolder.png", 1)
    addPosts(str("Teleseryi"), teleseryi_url, "DefaultFolder.png", 1)
    return

def sitePage(url):
    match_teleseryi = re.compile("teleseryi.info").findall(url)
    match_pinoytvshows = re.compile("pinoytvshows.me").findall(url)
    match_magtvnaph = re.compile("magtvnaph.com").findall(url)
    if match_teleseryi:
        firstPage_teleseryi(url)
    if match_pinoytvshows:
        firstPage_pinoytvshows(url)
    if match_magtvnaph:
        firstPage_magtvnaph(url)
    return

def listPage(url):
    match_teleseryi = re.compile("teleseryi.info").findall(url)
    match_pinoytvshows = re.compile("pinoytvshows.me").findall(url)
    match_magtvnaph = re.compile("magtvnaph.com").findall(url)
    if match_teleseryi:
        listPage_teleseryi(url)
    if match_pinoytvshows:
        listPage_pinoytvshows(url)
    if match_magtvnaph:
        listPage_magtvnaph(url)
    return

def firstPage_teleseryi(url):
    html = getHTML(urllib.unquote_plus(url))
    # https://bugs.launchpad.net/beautifulsoup/+bug/838022
    BeautifulSoup.NESTABLE_TAGS['td'] = ['tr', 'table']
    soup = BeautifulSoup(html)
    thumbs = soup.findAll('div','thumb')
    lcount = 0
    # Items
    for links in soup.findAll('h2','post-title entry-title'):
        script = thumbs[lcount].find('script')
        try:
            thumbnail_container = script.contents[0]
        except:
            thumbnail = "DefaultFolder.png"
        try:
            tmatch = re.compile('document.write\(bp_thumbnail_resize\(\"(.+?)\",').findall(thumbnail_container)
        except:
            thumbnail = "DefaultFolder.png"
        try:
            thumbnail = tmatch[0]
        except:
            thumbnail = "DefaultFolder.png"
        lcount = lcount + 1
        for line in links.findAll('a'):
            try:
                title = links.find('a').contents[0].strip()
            except:
                title = "No title"
            try:
                link = links.find('a')['href']
            except:
                link = None
            if title and link:
                if teleseryi_url in link:
                    addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), thumbnail, 0)
    olderlinks = soup.find('a', 'blog-pager-older-link')
    try:
        title = olderlinks.contents[0]
    except:
        title = "Mga Lumang mga Post"
    try:
        link = olderlinks.attrs[1][1]
    except:
        link = None
    if title and link:
        addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), "DefaultFolder.png", 1)
    return

def firstPage_pinoytvshows(url):
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
            addPosts(title, link, thumbnail, 0)
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

def firstPage_magtvnaph(url):
    firstmatch = re.compile('www.magtvnaph.com$').findall(url)
    absmatch = re.compile('Abs-cbn').findall(url)
    gmamatch = re.compile('Gma%207').findall(url)
    gma_url = 'http://www.magtvnaph.com/search/label/Gma%207'
    abs_url = 'http://www.magtvnaph.com/search/label/Abs-cbn'
    if firstmatch:
        addPosts(str("GMA TV Shows"), gma_url, "DefaultFolder.png", 1)
        addPosts(str("ABS-CBN Shows"), abs_url, "DefaultFolder.png", 1)
    else:
        html = getHTML(urllib.unquote_plus(str(url)).replace(' ','%20'))
        BeautifulSoup.NESTABLE_TAGS['td'] = ['tr', 'table']
        soup = BeautifulSoup(str(html))
        for article in soup.findAll('article','post hentry'):
                h2 = article.find('h2', 'post-title entry-title')
                try:
                    title = h2.find('a').contents[0].strip()
                except:
                    title = "No title"
                try:
                    link = h2.find('a')['href']
                except:
                    link = None
                try:
                    thumbnail = article.find('img')['src']
                except:
                    thumbnail = "DefaultFolder.png"
                if title and link:
                    addPosts(title, link, thumbnail, 0)
        olderlinks = soup.find('a', 'blog-pager-older-link')
        try:
            title = olderlinks.contents[0]
        except:
            title = "Older Posts"
        try:
            link = olderlinks.attrs[1][1]
        except:
            link = None
        if title and link:
            addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), "DefaultFolder.png", 1)
    return

def listPage_teleseryi(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(html)
    links = []
    # Items
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
    tab1 = soup.find('div', attrs={'id': 'tabs-1'})
    headings = tab1.findAll('h3')
    iframes = tab1.findAll('iframe')
    hcnt = 0
    for heading in headings:
        lurl = tab1.findAll('iframe')[hcnt]['src']
        url = get_vidlink(lurl)
        links.append(str(url))
        hcnt = hcnt + 1
    if (len(links) > 1):
        durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': title, 'thumbnail': thumbnail, 'title': title})
        itemname = 'Play All Parts'
        li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
        li.setInfo(type="Video",infoLabels={"Title": title, "Plot" : "All parts of" + title})
        li.setProperty('fanart_image', thumbnail)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=durl, listitem=li)
    hcnt = 0
    for heading in headings:
        ititle = heading.contents[0]
        url = links[hcnt]
        thumb = thumbnail
        plot = ititle + ' of ' + title
        listitem=xbmcgui.ListItem(ititle, iconImage=thumb, thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot })
        listitem.setProperty("IsPlayable", "true")
        listitem.setProperty("fanart_image", thumb)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
        hcnt = hcnt + 1
    return

def listPage_pinoytvshows(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(html)
    links = []
    # Items
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
    iframes = soup.findAll('iframe')
    hcnt = 0
    for iframe in iframes:
        lurl = iframe['src']
        url = get_vidlink(lurl)
        links.append(str(url))
        hcnt = hcnt + 1
    if (len(links) > 1):
        durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': title, 'thumbnail': thumbnail, 'title': title})
        itemname = 'Play All Parts'
        li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
        li.setInfo(type="Video",infoLabels={"Title": title, "Plot" : "All parts of" + title})
        li.setProperty('fanart_image', thumbnail)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=durl, listitem=li)
    hcnt = 0
    for iframe in iframes:
        partcnt = hcnt + 1
        ititle = "Part " + str(partcnt)
        url = links[hcnt]
        thumb = thumbnail
        plot = ititle + ' of ' + title
        listitem=xbmcgui.ListItem(ititle, iconImage=thumb, thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot })
        listitem.setPath(url)
        listitem.setProperty("IsPlayable", "true")
        listitem.setProperty("fanart_image", thumb)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
        hcnt = hcnt + 1
    return

def listPage_magtvnaph(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(html)
    links = []
    # Items
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
    iframes = soup.findAll('iframe')
    hcnt = 0
    for iframe in iframes:
        lurl = iframe['src']
        url = get_vidlink(lurl)
        links.append(str(url))
        hcnt = hcnt + 1
    if (len(links) > 1):
        durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': title, 'thumbnail': thumbnail, 'title': title})
        itemname = 'Play All Parts'
        li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
        li.setInfo(type="Video",infoLabels={"Title": title, "Plot" : "All parts of" + title})
        li.setProperty('fanart_image', thumbnail)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=durl, listitem=li)
    hcnt = 0
    for iframe in iframes:
        partcnt = hcnt + 1
        ititle = "Part " + str(partcnt)
        url = links[hcnt]
        thumb = thumbnail
        plot = ititle + ' of ' + title
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
    match_linksharetv = re.compile('http://www.linkshare.tv/mp4/\?url').findall(url)
    match_linksharetvplay = re.compile('http://www.linkshare.tv/play/\?url').findall(url)
    match_dailymotion = re.compile('www.dailymotion.com').findall(url)
    match_videorss = re.compile('http://videorss.net/mp4/\?url').findall(url)
    match_pinoytvshows = re.compile('www.pinoytvshows.me').findall(url)
    match_youtube = re.compile('www.youtube.com').findall(url)
    match_vimeo = re.compile('player.vimeo.com').findall(vidlink)
    if match_vimeo:
        vidlink = get_vidlink_vimeo(vidlink)
    if match_linksharetv:
        vidlink = get_vidlink_linksharetv(url)
    if match_linksharetvplay:
        vidlink = get_vidlink_linksharetvplay(url)
        match_vimeo_in = re.compile('player.vimeo.com').findall(vidlink)
        if match_vimeo_in:
            vidlink = get_vidlink_vimeo(vidlink)
    if match_dailymotion:
        vidlink = get_vidlink_dailymotion(url)
    if match_videorss:
        vidlink = get_vidlink_linksharetv(url)
    if match_pinoytvshows:
        vidlink = get_vidlink_pinoytvshows(url)
        match_youtube_in = re.compile('www.youtube.com').findall(vidlink)
        if match_youtube_in:
            vidlink = get_vidlink_youtube(vidlink)
    if match_youtube:
        vidlink = get_vidlink_youtube(url)
    return vidlink

def get_vidlink_dailymotion(url):
    vidlink = ''
	# check if URL starts with just // and not the usual http: or https:; add 'http' accordingly
    dblslshpat = re.compile("//")
    if (dblslshpat.match(url, 0) > -1):
        url = "http:"+url
    html = getHTML(url)
    soup = BeautifulSoup(html)
    scripts = soup.findAll('script')
    scode = scripts[8].contents[0]
    matchconfig = re.compile('var config = (\{.+?\})\;').findall(scripts[8].contents[0])
    json_string = matchconfig[0]
    parsed_json = json.loads(json_string)
    fileurl = parsed_json['metadata']['qualities']['auto'][0]['url']
    lastquality = 0
    for q in parsed_json['metadata']['qualities']:
        if q == 'auto':
            continue
        if int(lastquality) > int(q):
            continue
        else:
            try:
                fileurl = parsed_json['metadata']['qualities'][q][1]['url']
            except:
                try:
                    fileurl = parsed_json['metadata']['qualities'][q][0]['url']
                except:
                    continue
            lastquality = int(q)
    vidlink = fileurl
    return vidlink

def get_vidlink_linksharetv(url):
    urlmatch = re.search('(?<=\=).+', url)
    vidlink = urlmatch.group(0)
    return vidlink

def get_vidlink_linksharetvplay(url):
    html = getHTML(urllib.unquote_plus(url))
    soup = BeautifulSoup(str(html))
    iframe = soup.find('iframe')
    vidlink = iframe['src']
    return vidlink

def get_vidlink_vimeo(url):
    match=re.compile('https://player.vimeo.com/video/(.+)\?').findall(url)
    vid = match[0]
    vidlink="plugin://plugin.video.vimeo/play/?video_id="+vid
    return vidlink

def get_vidlink_pinoytvshows(url):
    html = getHTML(urllib.unquote_plus(url))
    match = re.compile('file: "(.+?)"', re.DOTALL).findall(html)
    try:
        vidlink = match[0]
    except:
        vidlink = ''
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
        match=re.compile('https://www.youtube.com/watch\?v=(.+)').findall(url)
        vidlink=getYoutube(match[0])
        if vidlink == "":
            vidlink="plugin://plugin.video.youtube/?action=play_video&videoid="+match[0]
    return vidlink

def getYoutube(code):
    yturl = 'http://www.youtube.com/watch?v='+code+'&fmt=18'
    link = getHTML(yturl)
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

def addPosts(title, url, thumbnail, first):
    listitem=xbmcgui.ListItem(title, iconImage=thumbnail)
    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot" : title } )
    if first == 1:
        xurl = "%s?otherpage=True&url=" % sys.argv[0]
    else:
        xurl = "%s?list=True&url=" % sys.argv[0]
    xurl = xurl + url
    listitem.setPath(xurl)
    listitem.setProperty("fanart_image", thumbnail)
    folder = True
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=folder)

def play_all_videos(videoType, videoIds, thumbnail, title):
    notify("Playing all parts.")
    cntr = 1
    totl = len(videoIds)
    xbmcPlayer = xbmc.Player()
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    for videoId in videoIds:
        list_title = title +" ["+ str(cntr) +" of "+ str(totl) +"]"
        listitem = xbmcgui.ListItem(list_title)
        listitem.setThumbnailImage(thumbnail)
        playlist.add(videoId, listitem)
        cntr = cntr + 1
    xbmcPlayer.play(playlist)
    return 0

def notify(msg):
    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')
    __icon__ = __addon__.getAddonInfo('icon')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, msg, 4000, __icon__))
    return 0

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

def build_url(query):
    return thebase + '?' + urllib.urlencode(query)

if (__name__ == "__main__" ):
    if (not sys.argv[2]):
        firstPage()
    else:
        params = getParameters(sys.argv[2])
        get = params.get
        mode = ''
        mode = get("mode")
        if (get("list")):
            listPage(get("url"))
        if (get("otherpage")) and not (get("mode")):
            sitePage(get("url"))
        if (mode == "playAllVideos"):
            thebase = sys.argv[0]
            foldername = args['foldername'][0]
            url = args['url'][0]
            thumbnail = args['thumbnail'][0]
            title = args['title'][0]
            url = url.replace("[","").replace("]","").replace("'","")
            urls = url.split(", ")
            play_all_videos(thebase,urls,thumbnail,title)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
