# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import scrapy
from scrapy.exceptions import CloseSpider

import requests
import time
import yaml
import ast
import json
import pymysql
import urllib
import copy
import re
from bihu.items import ArticleItem
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg

class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ["bihu.com"]
    def __init__(self, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)

        self.start_number    = int(xzcfg._get('spider', 'start_number'))
        self.max_number      = int(xzcfg._get('spider', 'max_number'))
        self.next_start_number = self.start_number

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
        #self.url = 'https://be01.bihu.com/bihu-be/api/content/show/getArticle'
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

    def start_requests(self):
        effect_row = 0

        #self.start_number = 3163
        #while self.start_number < 3164:
        while self.start_number < self.max_number:
            artid = str(self.start_number)

            formdata = {
                'userId'     : '',
                'accessToken': '',
                'artId'      : artid
            }
            cursor = self.__db.cursor()
            try:
                sql = 'select 1 from %s where artid = %s limit 1;' % ( self.__article_table, artid )
                effect_row = cursor.execute(sql)
                print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
                print effect_row
                print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS"
            except BaseException as e:
                xzlog.error(e)
            cursor.close()

            if effect_row == 0:
                xzlog.info("start to download article, artid[%s]" % artid)
                #mymeta = {'proxy_index': 1, 'change_proxy': False, 'artid': artid}
                mymeta = {'artid': artid}
                yield scrapy.FormRequest(self.url, callback=self.parse_item, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)
            else:
                xzlog.info("skip article due to exited in DB, artid[%s]" % artid)

            self.start_number = self.start_number + 1

        self.__db.close()
        # write start number back to config.ini file
        # we will start to crawl from this start_number for next time
        time.sleep(10)
        new_start_number = str(self.next_start_number)
        new_max_number = str(self.next_start_number+self.max_number)
        xzlog.info("write new start_number[%s] and max_number[%s] back to config file" %(new_start_number, new_max_number))
        xzcfg._set('spider', 'start_number', new_start_number)
        xzcfg._set('spider', 'max_number', new_max_number)
        xzlog.info("write done!")

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
            #raw_data= ast.literal_eval(raw_str)
            # TODO
            # Could not find a good method to do convert
            # Maybe YAML load failed due to special character such as #x1f44d
            # Just skip it right now:<
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
            self.next_start_number = int(raw_data['data']['id'])
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
            yield scrapy.FormRequest(self.url, callback=self.parse_item, formdata=formdata, headers=self.headers, meta=mymeta, method='POST', dont_filter = True)
            #raise CloseSpider('请求过于频繁。')
        else:
            xzlog.error("unkown data structure! raw_str[%s]" % raw_str)
            raise CloseSpider('unkown data structure')

    def to_utf8(self, mystr):
        if isinstance(mystr, unicode):
            return urllib.unquote(mystr).encode('utf-8')
        elif isinstance(mystr, str):
            return urllib.unquote(mystr)
        else:
            raise CloseSpider('unkonwn string type')

