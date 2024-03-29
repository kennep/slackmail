#!/usr/bin/env python3
import sys
import traceback
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import configparser
import argparse
import time
import select

DEFAULT_LOGFILE = '/var/log/slackmail.log'
DEFAULT_CONFIGFILE = '/etc/slackmail.conf'
def read_config(filename):
    config = configparser.ConfigParser()
    if not config.has_section('log'):
        config.add_section('log')
    config.set('log', 'logfile', DEFAULT_LOGFILE)
    config.read_file(open(filename, 'r'))
    return config

parser = argparse.ArgumentParser(description='Send stadard out to slack')
parser.add_argument('--config', dest='configfile', action='store',
                    default=DEFAULT_CONFIGFILE,
                    help='Config file to read (default %s)' % DEFAULT_CONFIGFILE)
parser.add_argument('--username', dest='username', action='store',
    default=None,
    help='Username to post as')
parser.add_argument('--channel', dest='channel', action='store',
    default=None,
    help='Channel to post to')
parser.add_argument('--tee', dest='tee', action='store_true',
    default=False,
    help='Also send output to standard out')

args = parser.parse_args()

config = read_config(args.configfile)
logfile = config.get('log', 'logfile')
webhook_url = config.get('slack', 'webhook_url')

linebuffer = []
last_send = 0

def flush(linebuffer):
    if not linebuffer: return
    try:
        payload = {
            'text': "".join(linebuffer),
            'icon_emoji': ':robot_face:'
        }
        if args.username is not None:
            payload['username'] = args.username
        if args.channel is not None:
            payload['channel'] = args.channel
        elif config.has_option('slack', 'channel'):
            payload['channel'] = config.get('slack', 'channel')
        payload = json.dumps(payload).encode('utf-8')
        urllib.request.urlopen(webhook_url, payload)
    except Exception as e:
        print("Error posting to Slack:", file=sys.stderr)
        traceback.print_exc()
        print("Payload:", file=sys.stderr)
        print(payload, file=sys.stderr)

while True:
    if linebuffer:
        (r,w,e) = select.select([sys.stdin], [], [], 2)
        if r:
            do_read = True
        else:
            do_read = False
    else:
        do_read = True

    if do_read:
        inputstring = sys.stdin.readline()
        if inputstring == '':
            flush(linebuffer)
            break
        if args.tee:
            print(inputstring, end=' ')
        linebuffer.append(inputstring)

    if time.time() - last_send < 2:
        continue
    flush(linebuffer)
    linebuffer = []
    last_send = time.time()
