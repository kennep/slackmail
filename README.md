Slackmail is a script that reads an email on standard input and sends it as a message on Slack.
You can integrate it with your mail transfer agent (sendmail, exim, postfix, etc.) so that you can
get mail from the server posted to a slack channel instead.

This repository also includes slackcat, a simple utility that will send whatever it gets on standard input,
to slack, on a line-by-line basis.

# Installation

To use it, you fist need to set up an incoming webhook integration on Slack.

Then, copy the `slackmail.py` script to a location of your choosing.

Copy `slackmail.conf.sample` to `/etc/slackmail.conf` and set the `webhook_url`
setting in that config file to the webhook URL.

Lastly, you need to configure the MTA to use slackmail.

For many MTAs, adding the following line in /etc/aliases is enough to get root's mail sent to slack:

`root: |/path/to/slackmail.py`

## Nullmailer support ##

This script can also function as a nullmailer protocol handler. Write a small wrapper script
that calls slackmail with the --nullmailer command line argument.

Example:

```
#!/bin/sh
exec /usr/local/bin/slackmail.py --nullmailer
```

This wrapper script should be installed alongside the smtp protocol handler. You can then
use the script name as a protocol name in nullmailer's `remotes` config file.

Example:

```
dummy-host-name slackmail
```

# slackcat
The slackcat utility just echoes to slack what it gets on standard input on a line-by-line
basis.

Example:

```
ls -l |python slackcat.py --tee --username ls
```

The --tee option also echoes what it gets on standard input, to standard output, while the
--username option lets you specify what username to post as (the default is to post as
  whatever username is set as the default for the webhook you have specified.)
