#!/usr/bin/env python3
import email
import email.header
import email.policy
import sys
import traceback
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import configparser
import argparse

DEFAULT_LOGFILE = '/var/log/slackmail.log'
DEFAULT_CONFIGFILE = '/etc/slackmail.conf'
def read_config(filename):
    config = configparser.ConfigParser()
    if not config.has_section('log'):
        config.add_section('log')
    config.set('log', 'logfile', DEFAULT_LOGFILE)
    config.read_file(open(filename, 'r'))
    return config

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

username = '(unknown)'

try:
    if args.nullmailer:
        # nullmailer protocol handlers expect the first line of input to be the sender,
        # then following lines to be recipients, then a blank line,
        # before the actual mail. We skip this before processing the
        # rest.
        idx = inputstring.find("\n\n")
        if idx == -1:
            raise ValueError("Input did not contain nullmailer prefix")
        inputstring = inputstring[idx+2:]

    message = email.message_from_string(inputstring, policy=email.policy.default)

    sender = message['from']
    subject = message['subject']
    if message.is_multipart():
        body = message.get_body(('plain',)).get_content()
    else:
        body = message.get_content()
    (realname, addr) = email.utils.parseaddr(sender)
    if realname:
        username = "%s <%s>" % (realname, addr)
    else:
        username = addr
    if isinstance(body, bytes):
        body = f"<{len(bytes)} binary bytes>"
except Exception:
    realname = "Error"
    subject = "Error parsing incoming mail"
    body = traceback.format_exc() + "\nIncoming message:\n\n" + inputstring

payload = ''.encode('utf-8')
try:
    payload = {
        'attachments': [{
          'title': subject,
          'text': '```\n' + body + '```\n',
          'mrkdwn_in': ["text"]
        }],
        'username': username,
        'icon_emoji': ':robot_face:'
    }
    if config.has_option('slack', 'channel'):
        payload['channel'] = config.get('slack', 'channel')
    payload = json.dumps(payload).encode('utf-8')
    urllib.request.urlopen(webhook_url, payload)
except Exception as e:
    print("Error posting to Slack:")
    traceback.print_exc()
    print("Payload:")
    print(payload)
    with open(logfile, 'a') as logfd:
        print(datetime.datetime.now(), file=logfd)
        print("Error posting to Slack:", file=logfd)
        print(traceback.format_exc(), file=logfd)
        print("Payload: ", file=logfd)
        print(payload, file=logfd)
