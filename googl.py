#!/usr/bin/python
#  Corey Goldberg - 2010
#
# goo.gl shortener
# http://coreygoldberg.blogspot.com/2010/10/python-shorten-url-using-googles.html
import json
import urllib
import urllib2


def shorten(url):
    gurl = 'http://goo.gl/api/url?url=%s' % urllib.quote(url.encode('utf-8'))
    req = urllib2.Request(gurl, data='')
    req.add_header('User-Agent', 'toolbar')
    results = json.load(urllib2.urlopen(req))
    return results['short_url']
