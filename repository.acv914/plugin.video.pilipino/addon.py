import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import xbmcplugin
import re
import urllib2
import urllib
import urlparse
import json
import random
from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer
addon_handle = sys.argv[1]
args = urlparse.parse_qs(sys.argv[2][1:])
thebase = sys.argv[0]

# the sources
teleserye_url = 'http://www.teleserye.su'
useragent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
referer = teleserye_url

def getHTML(url,useragent,referer):
    try:
        print 'getHTML :: url = ' + url
        req = urllib2.build_opener()
        if useragent != "":
          req.addheaders = [('User-Agent', useragent)]
        if referer != "":
          req.addheaders = [('Referer', referer)]
        response = req.open(url)
        link = response.read()
        response.close()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
    else:
        return link

def firstPage():
    addPosts(str("Teleserye"), teleserye_url, "DefaultFolder.png", 1)
    return

def sitePage(url):
    match_teleserye = re.compile("teleserye.su").findall(url)
    if match_teleserye:
        firstPage_teleserye(url)
    return

def listPage(url):
    match_teleserye = re.compile("teleserye.su").findall(url)
    if match_teleserye:
        listPage_teleserye(url,useragent,referer)
    return

def firstPage_teleserye(url):
    titles = {}
    links = {}
    backtrack = 6
    for i in range(1, backtrack):
      if i == 1:
        (titles, links) = getfirstPage_teleserye(url,useragent,referer)
      else: 
        urlx = url + '/page/' + str(i)
        (titlesx, linksx) = getfirstPage_teleserye(urlx,useragent,referer)
        titles.update(titlesx)
        links.update(linksx)
    for t in sorted(titles.keys(), reverse=True):
        title = titles[t]
        link = links[t]
        addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), "DefaultFolder.png", 0)
    return

def oldlistPage_teleserye(url):
    allurls = getallpages(url,useragent,referer)
    
    if (len(links) > 0):
        durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': title, 'thumbnail': thumbnail, 'title': title})
        itemname = 'Play All Parts'
        li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
        li.setInfo(type="Video",infoLabels={"Title": title, "Plot" : "All parts of" + title})
        li.setProperty('fanart_image', thumbnail)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=durl, listitem=li)
    hcnt = 0
    #for iframe in iframes:
    #    partcnt = hcnt + 1
    #    ititle = "Part " + str(partcnt)
    #    url = links[hcnt]
    #    thumb = thumbnail
    #    plot = ititle + ' of ' + title
    #    listitem=xbmcgui.ListItem(ititle, iconImage=thumb, thumbnailImage=thumb)
    #    listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot })
    #    listitem.setPath(url)
    #    listitem.setProperty("IsPlayable", "true")
    #    listitem.setProperty("fanart_image", thumb)
    #    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
    #    hcnt = hcnt + 1
    return


def getfirstPage_teleserye(url,useragent,referer):
    tlinks = {}
    llinks = {}
    html = getHTML(urllib.unquote_plus(str(url)).replace(' ','%20'),useragent,referer)
    #BeautifulSoup.NESTABLE_TAGS['td'] = ['tr', 'table']
    soup = BeautifulSoup(str(html))
    for article in soup.findAll('div','cat-hadding'):
            try:
                title = article.find('a')['title']
            except:
                title = "No title"
            try:
                link = article.find('a')['href']
            except:
                link = None
            try:
                thumbnail = article.find('img')['data-layzr']
            except:
                thumbnail = "DefaultFolder.png"
            if title and link:
            #    addPosts(title, link, thumbnail, 0)
                match_url = re.compile('http://www.teleserye.su/([^/]+?)/.+?$').findall(link)
                articleid = match_url[0]
                #alinks[title] = link
                #ilinks[title] = articleid
                tlinks[articleid] = title
                llinks[articleid] = link
            
    olderlinks = soup.find('a', 'blog-pager-older-link')
    try:
        title = olderlinks.contents[0]
    except:
        title = "Older Posts"
    try:
        link = olderlinks.attrs[1][1]
    except:
        link = None
    #if title and link:
        #addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), "DefaultFolder.png", 1)
    return(tlinks,llinks)

def listPage_teleserye(url,useragent,referer):
    #notify("yes")
    allurls = getallpages(url,useragent,referer)
    links = []
    for p in allurls:
        html = getHTML(urllib.unquote_plus(p),useragent,'')
        soup = BeautifulSoup(html)
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
        conurl = soup.find('iframe')['src']
        #turl = get_vidlink_disklinksharetvplay(conurl,useragent,referer)
        turl = get_vidlink(conurl,useragent,referer)
        links.append(str(turl))
    
    if (len(links) > 0):
        durl = build_url({'url': links, 'mode': 'playAllVideos', 'foldername': title, 'thumbnail': thumbnail, 'title': title})
        itemname = 'Play All Parts'
        li = xbmcgui.ListItem(itemname, iconImage=thumbnail)
        li.setInfo(type="Video",infoLabels={"Title": title, "Plot" : "All parts of" + title})
        li.setProperty('fanart_image', thumbnail)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=durl, listitem=li)
    hcnt = 0
    for l in links:
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
    return(links)

def get_vidlink(url,useragent,referer):
    match_linksharetv = re.compile('/linkshare.tv/mp4/').findall(url)
    if match_linksharetv:
        vidlink = get_vidlink_linksharetv(url,useragent,referer)
    else:
        vidlink = get_vidlink_disklinksharetvplay(url,useragent,referer)
    return vidlink

def get_vidlink_disklinksharetvplay(url,useragent,referer):
    #notify(referer)
    html = getHTML(urllib.unquote_plus(url),useragent,referer)
    soup = BeautifulSoup(str(html))
    #randomname = random.randint(1,100000001)
    #xfile = 'special://temp/' + str(randomname) + '.txt'
    #x = xbmcvfs.File(xfile, 'w')
    #wres = x.write(str(soup))
    #x.close()
    vidlink = soup.find('source')['src']
    filehtml = getHTML(vidlink,useragent,referer)
    xserver = re.sub('(/)[a-zA-Z0-9\.\-]+$', r'\1', vidlink, flags=re.DOTALL)
    newm3u8 = re.sub(r'\n([^#])', '\n' + xserver + r'/\1', filehtml, flags=re.DOTALL)
    randomname = random.randint(1,100000001)
    tfile = 'special://temp/' + str(randomname) + '.m3u8'
    f = xbmcvfs.File(tfile, 'w')
    wres = f.write(str(newm3u8))
    f.close()
    #return(newm3u8)
    return(tfile)

def get_vidlink_linksharetv(url,useragent,referer):
    html = getHTML(urllib.unquote_plus(url),useragent,referer)
    soup = BeautifulSoup(str(html))
    vidlink = soup.find('source')['src']
    return(vidlink)

def getallpages(url,useragent,referer):
    allurls = []
    lphtml = getHTML(urllib.unquote_plus(str(url)).replace(' ','%20'),useragent,referer)
    soup = BeautifulSoup(lphtml)
    center = soup.find('center')
    alllps = center.findAll('a')
    allurls.append(url)
    for part in alllps:
        parturl = part['href']
        allurls.append(parturl)
    return(allurls)

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
