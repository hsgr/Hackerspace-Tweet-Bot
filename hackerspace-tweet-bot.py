#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Tweeting bot for hackerspace events
#
import urllib
import smtplib
import htmllib
import json
import string
from datetime import datetime, timedelta

import googl

# Config Section Start
USERNAME = None
PASSWORD = None
TWEET = False
MAIL = False
MAIL_FROM = 'noreply@hackerspace.gr'
MAIL_TO = 'announce@hackerspace.gr'
MAIL_KEY = None
# Config Section End

QUERY = "http://hackerspace.gr/api.php?action=ask&q=[[Category:Events]]" \
        "&format=json&po=location|Start%20date|"

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

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

def main():
    email_sender = smtplib.SMTP('localhost')
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

        when = None
        if sameday(today, start_date):
            when = u"Σήμερα"

        elif sameday(tomorrow, start_date):
            when = u"Αύριο"

        if when:
            # shorten url
            # url-quote wiki page title so we
            # generate correct links
            url = googl.shorten(item['uri'][:43] +\
                                urllib.quote(item['uri'][43:])
                                ).encode("utf-8")
            title = unescape(item['title'])

            tweet_message = u"%s στις %02d.%02d: %s %s" %\
                            (when,
                             start_date.hour,
                             start_date.minute,
                             truncate(title, 140),
                             url
                             )
            tweet_message = tweet_message.encode("utf-8")
            email_message = u"%s στις %02d.%02d: %s" %\
                            (when,
                             start_date.hour,
                             start_date.minute,
                             title
                             )
            email_message = email_message.encode("utf-8")

            if TWEET:
                squawk(USERNAME, PASSWORD, tweet_message)

            if MAIL:
                BODY = string.join(("Approved: %s" % MAIL_KEY,
                                    "From: %s" % MAIL_FROM,
                                    "To: %s" % MAIL_TO,
                                    "Subject: [hsgr-ann] %s" % email_message,
                                    "",
                                    email_message,
                                    u"\r\nΠερισσότερα: ".encode("utf-8") + url,
                                    "\r\n--\r\nHackerspace Little Event Bot",
                                    ), "\r\n"
                                   )
                email_sender.sendmail(MAIL_FROM, MAIL_TO, BODY)

if __name__ == "__main__":
    main()
