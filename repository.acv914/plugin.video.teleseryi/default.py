import xbmc
import xbmcgui
import xbmcplugin
import re
import urllib2
import urllib
import json

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
        ititle = heading.contents[0]
        lurl = tab1.findAll('iframe')[hcnt]['src']
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