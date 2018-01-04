import xbmc
import xbmcgui
import xbmcplugin
import re
import urllib2
import urllib
import math

BASE_URL = "http://www.teleseryi.info"
 
from BeautifulSoup import MinimalSoup as BeautifulSoup, SoupStrainer

def getHTML(url):
        try:
            print 'getHTML :: url = ' + url
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
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
    tab1 = soup.find('div', attrs={'id': 'tabs-1'})
    headings = tab1.findAll('h3')
    iframes = tab1.findAll('iframe')
    hcnt = 0
    for heading in headings:
        title = heading.contents[0]
        lurl = tab1.findAll('iframe')[hcnt]['src']
        url = get_vidlink(lurl)
        thumb = "DefaultFolder.png"
        plot = "plot"
        time = "time"
        listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={ "Title": title, "Plot" : plot, "Duration" : time })
        listitem.setPath(url)
        listitem.setProperty("IsPlayable", "true")
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
    match=re.compile('http://www.dailymotion.com/embed/video/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/video/(.+?)&dk;').findall(url+"&dk;")
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/swf/(.+?)\?').findall(url)
    if(len(match) == 0):
        match=re.compile('http://www.dailymotion.com/embed/video/(.+?)$').findall(url)
    link = 'http://www.dailymotion.com/embed/video/'+str(match[0])
    req = get_page(link)
    req = req.encode("UTF-8")
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
    # Items
    for links in soup.findAll('h2','post-title entry-title'):
        for line in links.findAll('a'):
            try:
                title = links.find('a').contents[0]
            except:
                title = "No title"
            try:
                link = links.find('a')['href']
            except:
                link = None
            if title and link:
                if BASE_URL in link:
                    addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), 0)

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
        addPosts(str(title), urllib.quote_plus(link.replace('&amp;','&')), 1)
    return

def addPosts(title, url, first):
 listitem=xbmcgui.ListItem(title, iconImage="DefaultFolder.png")
 listitem.setInfo( type="Video", infoLabels={ "Title": title } )
 if first == 1:
    xurl = "%s?otherpage=True&url=" % sys.argv[0]
 else:
    xurl = "%s?next=True&url=" % sys.argv[0]
 xurl = xurl + url
 listitem.setPath(xurl)
 folder = True
 xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=folder)

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