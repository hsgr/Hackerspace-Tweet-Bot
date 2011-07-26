#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Tweeting bot for hackerspace events
#
import urllib
from datetime import datetime, timedelta
import json
import googl

USERNAME = None
PASSWORD = None

def sameday(d1, d2):
    # hmm maybe there is a function for this, but right now the
    # temperature is too high to check ;)
    # at least do it in a cool way
    attr = ('day', 'year', 'month')
    return reduce(lambda x,y: x==y==True,
                  map(lambda a: getattr(d1,a) == getattr(d2,a), attr)
                  )

def truncate(string,target):
    if len(string) > target:
        return string[:(target-3)] + "..."
    else:
        return string

def squawk(username,password,message):
    """Simple post-to-twitter function"""
    message = truncate(message,140) # trim message

    data = urllib.urlencode({"status" : message})
    res = urllib.urlopen("http://%s:%s@identi.ca/api/statuses/update.xml" %\
                         (username,password), data)

    return res

QUERY = "http://hackerspace.gr/api.php?action=ask&q=[[Category:Events]]" \
        "&format=json&po=location|Start%20date|"

today = datetime.now()
tomorrow = datetime.now() + timedelta(days=1)

try:
    results = urllib.urlopen(QUERY).read()
except:
    raise

results = json.loads(results)

try:
    data = results['ask']['results']['items']
except KeyError:
    raise ValueError("Bad API data")

for item in data:
    try:
        start_date = datetime.strptime(item['properties']['start_date'],
                                       "%Y-%m-%d %H:%M:%S"
                                       )
    except ValueError:
        # cannot parse date, move to next time
        continue

    message = None
    if sameday(today, start_date):
        message = u"Σήμερα στις %02d.%02d: %s %s" %\
                   (start_date.hour,
                    start_date.minute,
                    truncate(item['title'], 140),
                    googl.shorten(item['uri'])
                    )

    elif sameday(tomorrow, start_date):
        message = u"Αύριο στις %02d.%02d: %s %s" %\
                   (start_date.hour,
                    start_date.minute,
                    truncate(item['title'], 140),
                    # shorten url
                    # url-quote wiki page title so we
                    # generate correct links
                    googl.shorten(item['uri'][:43] +\
                                  urllib.quote(item['uri'][43:])
                                  )
                    )

    if message:
        squawk(USERNAME, PASSWORD, message.encode("utf-8"))


