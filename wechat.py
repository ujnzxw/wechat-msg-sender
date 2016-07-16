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
from lib.csflog import csflog
from lib.csfcfg import csfcfg
sys.setdefaultencoding( "utf-8" )

class WeChat(object):
    __token_id = ''
    # Init attribute
    def __init__(self, toparty, touser, msg):
        csfcfg._init('../cfg-private/cfg.ini')
        csflog.init_logger(csfcfg._get('logs', 'logfile'))

        self.__url    = csfcfg._get('server', 'url').rstrip('/')
        self.__corpid = csfcfg._get('server', 'corpid')
        self.__secret = csfcfg._get('server', 'secret')
        self.__toparty= toparty
        self.__touser = touser
        self.__msg    = msg

    """
    @Summary   : get token id by using
               : self.__url, self.__corpid, self.__secret
    @Parameter : url_prefix='/'
    @Attention : the token will fill into self.__token_id
    """
    def get_token(self, url_prefix='/'):

        params = {
                    'corpid'    : self.__corpid,
                    'corpsecret': self.__secret
                 }
        data = urllib.urlencode(params)
        url = self.__url + url_prefix + 'gettoken?'

        try:
            response = urllib2.Request(url + data)
        except KeyError:
            raise KeyError
        result = urllib2.urlopen(response)
        content = json.loads(result.read())

        try:
            self.__token_id = content['access_token']
        except KeyError:
            raise KeyError

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
                        csflog.error( 'reason: %s' % e.reason )
                elif hasattr(e,'code'):
                        csflog.error( 'code: %s' % e.code )
                return 0
        else:
                resp = json.loads(rtn.read())
                rtn.close()
        return resp

    """
    @Summary   : message sending method
    @Parameter : null
    @Attention : null
    """
    def send_msg(self):

        self.get_token()

        # Use default toparty if toparty is null
        if (self.__toparty == None):
            self.__toparty = csfcfg._get('user', 'toparty')

        csflog.info("touser - %s" % self.__touser)
        csflog.info("toparty - %s" % self.__toparty)

        data = json.dumps(
                {
                     'touser' : self.__touser,
                     'toparty': self.__toparty,
                     'msgtype': csfcfg._get('user', 'msgtype'),
                     'agentid': csfcfg._get('user', 'agentid'),
                     'text'   : { 'content' : self.__msg },
                     'safe'   : csfcfg._get('user', 'safe')
                },
                ensure_ascii = False)

        response = self.post_data(data)
        csflog.info(response)

if __name__ == '__main__':
        wechat = WeChat("ujnzxw", "Hello wechat!")
        wechat.send_msg()
