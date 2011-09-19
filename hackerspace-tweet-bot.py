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

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

import googl

#Read configuration
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
if parser.read('./config.ini'):
    USERNAME = parser.get('identica', 'username')
    PASSWORD = parser.get('identica', 'password')
    TWEET = parser.get('identica', 'tweet')
    MAIL = parser.get('email', 'mail')
    MAIL_FROM = parser.get('email', 'mail_from')
    MAIL_TO = parser.get('email', 'mail_to')
    MAIL_KEY = parser.get('email', 'mail_key')
else:
    print "error: no config.ini found"
    exit()

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
                msg = MIMEMultipart()
                msg.set_charset('utf-8')
		msg['Approved'] = MAIL_KEY
                msg['From'] = MAIL_FROM
                msg['To'] = MAIL_TO
                msg['Subject'] = '[hsgr-ann] %s' % email_message


                BODY = string.join(
                    (email_message,
                     u"\r\nΠερισσότερα: ".encode("utf-8") + url,
                     "\r\n--\r\nHackerspace Little Event Bot",
                     ), "\r\n"
                    )
                t = MIMEText(BODY)
                t.set_charset('utf-8')
                msg.attach(t)

                # attach ICS
                part = MIMEBase('text', "calendar")
                part.set_payload(string.join(
                    (
                    "BEGIN:VCALENDAR",
                    "VERSION:2.0",
                    "PRODID:-//hsgr/handcal//NONSGML v1.0//EN",
                    "BEGIN:VEVENT",
                    "UID:%s@hsgr" % item['title'].encode('utf-8').replace(' ', '_'),
                    "DTSTAMP:%04d%02d%02dT%02d%02d00" % (start_date.year,
                                                          start_date.month,
                                                          start_date.day,
                                                          start_date.hour,
                                                          start_date.minute),
                    "ORGANIZER;CN=Hackerspace:MAILTO:mail@hackerspace.gr",
                    "DTSTART:%04d%02d%02dT%02d%02d00" % (start_date.year,
                                                          start_date.month,
                                                          start_date.day,
                                                          start_date.hour,
                                                          start_date.minute),

                    "SUMMARY:%s" % email_message,
                    "END:VEVENT",
                    "END:VCALENDAR"
                    ), "\r\n")
                )
                part.add_header('Content-Disposition',
                                'attachment; filename="event.ics"')

                part.set_charset('utf-8')
                msg.attach(part)

                email_sender.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())

if __name__ == "__main__":
    main()
