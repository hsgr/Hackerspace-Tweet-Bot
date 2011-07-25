#!/usr/bin/env python
#
# Tweeting bot for hackerspace events
#

import urllib2
from datetime import datetime, timedelta
import json


def sameday(d1, d2):
    # hmm maybe there is a function for this, but right now the
    # temperature is too high to check ;)
    # at least do it in a cool way
    attr = ('day', 'year', 'month')
    return reduce(lambda x,y: x==y==True,
                  map(lambda a: getattr(d1,a) == getattr(d2,a), attr)
                  )

QUERY = "http://hackerspace.gr/api.php?action=ask&q=[[Category:Events]]" \
        "&format=json&po=location|Start%20date"

today = datetime.now()
tomorrow = datetime.now() + timedelta(days=1)

try:
    results = urllib2.urlopen(QUERY).read()
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

    if sameday(today, start_date):
        print "Today", item['title'], item['properties']['start_date']

    elif sameday(tomorrow, start_date):
        print "Tomorrow", item['title'], item['properties']['start_date']

