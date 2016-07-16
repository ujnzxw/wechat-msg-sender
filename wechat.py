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
import sys
reload(sys)
from lib.csflog import csflog
sys.setdefaultencoding( "utf-8" )

class WeChat(object):
    __token_id = ''
    # Init attribute
    def __init__(self,url):
        csflog.init_logger("./logs/wechat.log")
        self.__url = url.rstrip('/')
        self.__corpid = 'wx89bc331bff1b27fe'
        self.__secret = '2uBB853V9sTgNVr1mq-tUwccV_dJDqC_kqgU-Pu_Nycr0WH9lm26QyZsJO1Y5T7e'

    """
    @Summary   : get token id by using self.__url, self.__corpid, self.__secret
    @Parameter : url_prefix='/'
    @Attention : the token will fill into self.__token_id
    """
    def get_token(self, url_prefix='/'):

        params = {'corpid':self.__corpid, 'corpsecret':self.__secret}
        data = urllib.urlencode(params)

        url = self.__url + url_prefix + 'gettoken?'
        csflog.info("The link is %s" %(url + data))
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
    @Parameter : touser - the user you want to send to
               : message- the message contents
    @Attention : null
    """
    def send_msg(self,touser,message):

        self.get_token()

        data = json.dumps(
                {
                     'touser' : touser,
                     'toparty': "1",
                     'msgtype': "text",
                     'agentid': "1",
                     'text'   : { 'content' : message },
                     'safe'   : "0"
                },
                ensure_ascii=False)

        response = self.post_data(data)
        csflog.info(response)

if __name__ == '__main__':
        we_chat = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
        we_chat.send_msg(sys.argv[1],sys.argv[2])
