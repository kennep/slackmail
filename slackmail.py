#!/usr/bin/env python
import email
import email.header
import sys
import traceback
import json
import urllib2
import datetime
import ConfigParser
import argparse

DEFAULT_LOGFILE = '/var/log/slackmail.log'
DEFAULT_CONFIGFILE = '/etc/slackmail.conf'
def read_config(filename):
    config = ConfigParser.RawConfigParser()
    if not config.has_section('log'):
        config.add_section('log')
    config.set('log', 'logfile', DEFAULT_LOGFILE)
    config.readfp(open(filename, 'r'))
    return config

def decode_header(header):
    def decoder(t):
        (data, charset) = t
        if charset is None: return data
        else: return data.decode(charset).encode('utf-8')

    data = email.header.decode_header(header)
    return ''.join(map(decoder, data))

parser = argparse.ArgumentParser(description='Send mail to slack')
parser.add_argument('--config', dest='configfile', action='store',
                    default=DEFAULT_CONFIGFILE,
                    help='Config file to read (default %s)' % DEFAULT_CONFIGFILE)
parser.add_argument('--nullmailer', dest='nullmailer', action='store_true',
                    help='Work as a nullmailer protocol handler')

args = parser.parse_args()

config = read_config(args.configfile)
logfile = config.get('log', 'logfile')
webhook_url = config.get('slack', 'webhook_url')

inputstring = sys.stdin.read()

try:
    if args.nullmailer:
        # nullmailer protocol handlers expect the first line of input to be the sender,
        # then following lines to be recipients, then a blank line,
        # before the actual mail. We skip this before processing the
        # rest.
        idx = inputstring.find("\n\n")
        if idx == -1:
            raise ValueError, "Input did not contain nullmailer prefix"
        inputstring = inputstring[idx+2:]

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
    urllib2.urlopen(webhook_url, payload)
except Exception, e:
    print "Error posting to Slack:"
    traceback.print_exc()
    print "Payload:"
    print payload
    with open(logfile, 'a') as logfd:
        print >>logfd, datetime.datetime.now()
        print >>logfd, "Error posting to Slack:"
        print >>logfd, traceback.format_exc()
        print >>logfd, "Payload: "
        print >>logfd, payload
