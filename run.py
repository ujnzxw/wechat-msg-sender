#!/usr/bin/env python
#======================================================
# Title             : run.py
# Description       : runner
# Author            : ujnzxw
# Date              : 2016-07-16
# Version           : 0.0.1
# Usage             : python run.py -h
# Notes:            :
#======================================================
from wechat import WeChat
from optparse import OptionParser

REQUIRED_OPTIONS = {
                    ('touser', 'touser'),
                    ('message', 'message')
                   }
def run():
    usage = 'usage: %prog --touser=<to user> --message=<sending message> [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('--touser', '-u', dest='touser',
                      help='message send to')
    parser.add_option('--message', '-m', dest='message',
                      help='message you want to send')
    parser.add_option('--toparty', dest='toparty',
                      help='sending party. Use the one in cfg.ini as default')
    (options, args) = parser.parse_args()
    for option_name, key in REQUIRED_OPTIONS:
        if not getattr(options, key, None):
            raise ValueError('Missing required argument: '+option_name)

    wechat = WeChat(toparty=options.toparty,
                    touser=options.touser,
                    msg=options.message)


    wechat.send_msg()
