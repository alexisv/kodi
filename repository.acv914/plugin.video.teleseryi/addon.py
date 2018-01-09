import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import re
import urllib2
import urllib
import urlparse
import json

BASE_URL = "http://www.teleseryi.info"
addon_handle = sys.argv[1]
args = urlparse.parse_qs(sys.argv[2][1:])
thebase = sys.argv[0]

from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer

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
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
        else:
            return link

def listPage(url):
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

def get_vidlink(url):
    vidlink = ''
    match_linksharetv = re.compile('http://www.linkshare.tv/mp4/\?url').findall(url)
    match_dailymotion = re.compile('www.dailymotion.com').findall(url)
    match_videorss = re.compile('http://videorss.net/mp4/\?url').findall(url)
    if match_linksharetv:
        vidlink = get_vidlink_linksharetv(url)
    if match_dailymotion:
        vidlink = get_vidlink_dailymotion(url)
    if match_videorss:
        vidlink = get_vidlink_linksharetv(url)
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

def nextPage(params):
    get = params.get
    url = get("url")
    return listPage(url)

def firstPage(url):
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
                if BASE_URL in link:
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

def addPosts(title, url, thumbnail, first):
    listitem=xbmcgui.ListItem(title, iconImage=thumbnail)
    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot" : title } )
    if first == 1:
        xurl = "%s?otherpage=True&url=" % sys.argv[0]
    else:
        xurl = "%s?next=True&url=" % sys.argv[0]
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
        firstPage(BASE_URL)
    else:
        params = getParameters(sys.argv[2])
        get = params.get
        mode = ''
        mode = get("mode")
        if (get("next")) and not (get("search")):
            nextPage(params)
        if (get("otherpage")) and not (get("mode")):
            firstPage(get("url"))
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
