#!/usr/bin/env python
import email
import email.header
import sys
import traceback
import json
import urllib2
import datetime

WEBHOOK_URL = 'YOUR_INCOMING_WEBHOOK_URL_HERE'
LOGFILE = '/var/log/slackmail.log'

inputstring = sys.stdin.read()

def decode_header(header):
    def decoder(t):
        (data, charset) = t
        if charset is None: return data
        else: return data.decode(charset).encode('utf-8')

    data = email.header.decode_header(header)
    return ''.join(map(decoder, data))

try:
    message = email.message_from_string(inputstring)

    sender = message['from']
    subject = decode_header(message['subject'])
    if message.is_multipart():
        bodymsg = message.get_payload(0)
        if bodymsg.get_content_type() == 'multipart/alternative':
            body = bodymsg.get_payload(0).get_payload(decode=True)
            charset = bodymsg.get_payload(0).get_charset()
        else:
            body = bodymsg.get_payload(decode=True)
            charset = bodymsg.get_charset()
    else:
        body = message.get_payload(decode=True)
        charset = message.get_charset()
    (realname, addr) = email.utils.parseaddr(sender)
    realname = decode_header(realname)
    if charset:
        body = body.decode(charset).encode('utf-8')
except Exception:
    realname = "Error"
    subject = "Error parsing incoming mail"
    body = traceback.format_exc() + "\nIncoming message:\n\n" + inputstring

try:
    payload = {
        'attachments': [{
          'title': subject,
          'text': '```\n' + body + '```\n',
          'mrkdwn_in': ["text"]
        }],
        'username': realname,
        'icon_emoji': ':robot_face:'
    }
    payload = json.dumps(payload)
    urllib2.urlopen(WEBHOOK_URL, payload)
except Exception, e:
    print "Error posting to Slack:"
    traceback.print_exc()
    print "Payload:"
    print payload
    with open(LOGFILE, 'a') as logfile:
        print >>logfile, datetime.datetime.now()
        print >>logfile, "Error posting to Slack:"
        print >>logfile, traceback.format_exc()
        print >>logfile, "Payload: "
        print >>logfile, payload

