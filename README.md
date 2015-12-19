Slackmail is a script that reads an email on standard input and sends it as a message on Slack.
You can integrate it with your mail transfer agent (sendmail, exim, postfix, etc.) so that you can
get mail from the server posted to a slack channel instead.

For many MTAs, adding the following line in /etc/aliases is enough to get root's mail sent to slack:

`root: |/path/to/slackmail.py`

To use it, you need to set up an incoming webhook integration on Slack. Copy the Webhook URL
from the configuration page and paste it into the top of the slackmail script.

