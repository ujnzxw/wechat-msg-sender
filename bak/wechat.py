#!/usr/bin/env python
#======================================================
# Title             : wechat.py
# Description       : wechat task
# Author            : ujnzxw
# Date              : 2016-07-05
# Version           : 0.1
# Usage             : python wechat.py to-user message-content
# Notes:            :
#======================================================

# -*- coding: utf-8 -*-
import urllib,urllib2,json
import sys;reload(sys)

from optparse import OptionParser
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg
sys.setdefaultencoding( "utf-8" )

class WeChat(object):
    __token_id = ''
    # Init attribute
    def __init__(self, toparty, touser, msg):
        xzcfg._init('./config.ini')
        xzlog.init_logger(xzcfg._get('logs', 'logfile'))

        self.__url    = xzcfg._get('server', 'url').rstrip('/')
        self.__appid = xzcfg._get('server', 'appid')
        self.__secret = xzcfg._get('server', 'secret')
        self.__toparty= toparty
        self.__touser = touser
        self.__msg    = msg

    """
    @Summary   : get token id
    @Parameter : url_prefix='/'
    @Attention : the token will fill into self.__token_id
    """
    def get_token(self, url_prefix='/'):
        content = {}
        params  = {
                    'grant_type' : 'client_credential',
                    'appid'      : self.__appid,
                    'secret'     : self.__secret
                  }

        data = urllib.urlencode(params)
        url = self.__url + url_prefix + 'token?'

        response = urllib.urlopen(url, data)
        content = json.loads(response.read())

        try:
            access_token = content['access_token']
        except KeyError:
            raise KeyError
        print access_token
        return access_token

    """
    @Summary   : Post data method
    @Parameter : data - the data you want to send (json format)
               : url_prefix='/'
    @Attention : null
    """
    def post_data(self,data,url_prefix='/'):

        # Get message sending url
        url = self.__url + url_prefix + \
              'message/send?access_token=%s' % self.__token_id

        request = urllib2.Request(url,data)
        try:
                rtn = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
                if hasattr(e,'reason'):
                        xzlog.error( 'reason: %s' % e.reason )
                elif hasattr(e,'code'):
                        xzlog.error( 'code: %s' % e.code )
                return 0
        else:
                resp = json.loads(rtn.read())
                rtn.close()
        return resp

    """
    @Summary   : message sending
    @Parameter : null
    @Attention : null
    """
    def send_msg(self):

        self.get_token()

        # Use default toparty if toparty is null
        if (self.__toparty == None):
            self.__toparty = xzcfg._get('user', 'toparty')

        xzlog.info("touser - %s" % self.__touser)
        xzlog.info("toparty - %s" % self.__toparty)

        data = json.dumps(
                {
                     'touser' : self.__touser,
                     'toparty': self.__toparty,
                     'msgtype': xzcfg._get('user', 'msgtype'),
                     'agentid': xzcfg._get('user', 'agentid'),
                     'text'   : { 'content' : self.__msg },
                     'safe'   : xzcfg._get('user', 'safe')
                },
                ensure_ascii = False)

        #response = self.post_data(data)
        #xzlog.info(response)

if __name__ == '__main__':
        wechat = WeChat(1, "ujnzxw", "Hello wechat!")
        wechat.send_msg()
