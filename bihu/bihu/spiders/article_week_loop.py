# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import scrapy
from scrapy.exceptions import CloseSpider

import requests
import time
import datetime
import yaml
import ast
import json
import pymysql
import urllib
import copy
import re
# from scrapy.contrib.spidermiddleware.httperror import HttpError
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from twisted.internet.error import ConnectionRefusedError
from bihu.items import ArticleItem
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg

class ArticleSpider(scrapy.Spider):
    name = 'article-week-loop'
    allowed_domains = ["bihu.com"]
    def __init__(self, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)

        self.__db_host       = xzcfg._get('database', 'host')
        self.__db_name       = xzcfg._get('database', 'bihu')
        self.__db_user       = xzcfg._get('database', 'bihu_user')
        self.__db_password   = xzcfg._get('database', 'bihu_password')
        self.__article_table = xzcfg._get('database', 'bihu_article_table')
        self.__db = pymysql.connect(
                host        = self.__db_host,
                user        = self.__db_user,
                passwd      = self.__db_password,
                db          = self.__db_name,
                charset     = "utf8",
                use_unicode = False
        )

        self.url = 'https://be02.bihu.com/bihube-pc/api/content/show/getArticle'
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '28',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            #'Host': 'be02.bihu.com',
            'Origin': 'https://bihu.com',
            #'Referer': 'https://bihu.com/article/1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        self.start_artid    = self.get_start_artid()
        self.end_artid      = self.get_end_artid(self.start_artid)

    def start_requests(self):
        while self.start_artid < self.end_artid:
            artid = str(self.start_artid)
            formdata = {
                'userId'     : '',
                'accessToken': '',
                'artId'      : artid
            }
            xzlog.info("start to download article, artid[%s]" % artid)
            mymeta = {'artid': artid}
            yield scrapy.FormRequest(self.url, callback=self.parse_item, errback=self.parse_errback, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)

            self.start_artid = self.start_artid + 1

        self.__db.close()

    def parse_item(self, response):
        artid = response.meta['artid']
        formdata = {
            'userId'     : '',
            'accessToken': '',
            'artId'      : '%s' % str(artid)
        }

        text = response.text

        # remove emojis in content. due to:
        # yaml.load: unacceptable character #x1f440: special characters are not allowed
        # https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
        # https://stackoverflow.com/questions/31603075/how-can-i-represent-this-regex-to-not-get-a-bad-character-range-error/31605097#31605097
        #emoji_pattern = re.compile("["
        #        u"\U0001F600-\U0001F64F"  # emoticons
        #        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        #        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        #        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        #                           "]+", flags=re.UNICODE)
        emoji_pattern = re.compile(
            u"(\ud83d[\ude00-\ude4f])|"  # emoticons
            u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
            u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
            u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
            u"(\ud83c[\udde0-\uddff])"   # flags (iOS)
            "+", flags=re.UNICODE)
        raw_str = emoji_pattern.sub(r'', text) # no emoji

        try:
            raw_data= yaml.load(raw_str)
        except BaseException as e:
            xzlog.error("raw_str[%s], EX[%s]" % (raw_str, e))
            return
            #raise CloseSpider('load raw string to dict error! Ex: %s' % e)

        if raw_data['data'] is not None:
            item = ArticleItem()
            item['artid']     = raw_data['data']['id']
            item['title']     = self.to_utf8(raw_data['data']['title'])
            item['username']  = self.to_utf8(raw_data['data']['userName'])
            item['boardname'] = self.to_utf8(raw_data['data']['boardName'])
            item['userid']    = raw_data['data']['userId']
            item['updatime']  = raw_data['data']['updatime']
            item['content']   = self.to_utf8(raw_data['data']['content'])
            item['money']     = raw_data['data']['money']
            item['ups']       = raw_data['data']['ups']
            item['downs']     = raw_data['data']['downs']

            xzlog.success('download article info: resMsg[%s], artid[%s], title[%s]' %(raw_data['resMsg'],item['artid'],item['title']))
            yield item

        # {"data":null,"res":100004,"resMsg":"保存失败"}
        # {'res': 100004, 'data': None, 'resMsg': u'\u4fdd\u5b58\u5931\u8d25'}
        # 下面这种返回结果也是 “文章已删除或不存在”
        # {"data":null,"res":100004,"resMsg":""}

        elif raw_data['resMsg'] == u'\u4fdd\u5b58\u5931\u8d25' or \
             raw_data['resMsg'] == u'':
            item = ArticleItem()
            item['artid']     = artid
            item['title']     = '文章已删除或不存在'
            item['username']  = ''
            item['boardname'] = ''
            item['userid']    = ''
            item['updatime']  = ''
            item['content']   = ''
            item['money']     = ''
            item['ups']       = ''
            item['downs']     = ''
            #xzlog.success('ignore article info: resMsg[%s], artid[%s], title[%s]' %(raw_data['resMsg'],item['artid'],item['title']))
            xzlog.success('download article info: resMsg[%s], artid[%s], title[%s]' %(raw_data['resMsg'],item['artid'],item['title']))
            yield item

        #{"data":null,"res":0,"resMsg":"请求过于频繁。"}
        #{'res': 0, 'data': None, 'resMsg': u'\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41\u3002'}
        elif raw_data['resMsg'] == u'\u8bf7\u6c42\u8fc7\u4e8e\u9891\u7e41\u3002':
            xzlog.debug("download article faild due to anti-spider! resMsg[%s], artid[%s]"% (raw_data['resMsg'], artid))
            mymeta = copy.deepcopy(response.meta)
            mymeta['change_proxy']  = True
            yield scrapy.FormRequest(self.url, callback=self.parse_item, errback=self.parse_errback, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)
            #raise CloseSpider('请求过于频繁。')

        else:
            xzlog.error("unkown data structure! artid[%s], raw_str[%s]" % (artid, raw_str))
            raise CloseSpider('unkown data structure artid[%s], raw_str[%s]' % (artid, raw_str))

    #https://stackoverflow.com/questions/31146046/how-do-i-catch-errors-with-scrapy-so-i-can-do-something-when-i-get-user-timeout
    def parse_errback(self, failure):

        xzlog.error(repr(failure))
        request = failure.request

        artid = request.meta['artid']
        formdata = {
            'userId'     : '',
            'accessToken': '',
            'artId'      : '%s' % str(artid)
        }
        mymeta = copy.deepcopy(request.meta)
        mymeta['change_proxy']  = True


        if failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s' % request.url)

            xzlog.warning('Change proxy and re-request due to TimeoutError on %s' %  request.url)
            yield scrapy.FormRequest(self.url, callback=self.parse_item, errback=self.parse_errback, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)

        elif failure.check(ConnectionRefusedError):
            request = failure.request
            self.logger.error('ConnectionRefusedError on %s' % request.url)

            xzlog.warning('Change proxy and re-request due to TimeoutError on %s' %  request.url)
            yield scrapy.FormRequest(self.url, callback=self.parse_item, errback=self.parse_errback, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)

        elif failure.check(HttpError):
            request = failure.request
            self.logger.error('HttpError on %s' % request.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            xzlog.error('DNSLookupError on %s'% request.url)


    def to_utf8(self, mystr):
        if isinstance(mystr, unicode):
            return urllib.unquote(mystr).encode('utf-8')
        elif isinstance(mystr, str):
            return urllib.unquote(mystr)
        else:
            raise CloseSpider('unkonwn string type')

    def get_start_artid(self, delta_days=7):
        start_artid = 0
        seven_days_ago = datetime.datetime.today() - datetime.timedelta(days=delta_days)
        start_timestamp = int(time.mktime(seven_days_ago.timetuple()))
        sql = "select artid from article order by abs(%s - left(`updatime`,10)) limit 1;" % start_timestamp
        cursor = self.__db.cursor()
        try:
            cursor.execute(sql)
            (start_artid,) = cursor.fetchone()
        except BaseException as e:
            xzlog.error(e)
            raise CloseSpider('get start artid failed')
        cursor.close()
        return int(start_artid)

    def get_end_artid(self, start_artid):
        end_artid = start_artid + 30000
        return end_artid

