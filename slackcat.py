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

parser = argparse.ArgumentParser(description='Send stadard out to slack')
parser.add_argument('--config', dest='configfile', action='store',
                    default=DEFAULT_CONFIGFILE,
                    help='Config file to read (default %s)' % DEFAULT_CONFIGFILE)
parser.add_argument('--username', dest='username', action='store',
    default=None,
    help='Username to post as')
parser.add_argument('--tee', dest='tee', action='store_true',
    default=False,
    help='Also send output to standard out')

args = parser.parse_args()

config = read_config(args.configfile)
logfile = config.get('log', 'logfile')
webhook_url = config.get('slack', 'webhook_url')

while True:
    inputstring = sys.stdin.readline()
    if inputstring == '': break
    if args.tee:
        print inputstring,
    try:
        payload = {
            'text': inputstring.rstrip(),
            'icon_emoji': ':robot_face:'
        }
        if args.username is not None:
            payload['username'] = args.username
        if config.has_option('slack', 'channel'):
            payload['channel'] = config.get('slack', 'channel')
        payload = json.dumps(payload)
        urllib2.urlopen(webhook_url, payload)
    except Exception, e:
        print >> stderr, "Error posting to Slack:"
        traceback.print_exc()
        print >> stderr, "Payload:"
        print >> stderr, payload
