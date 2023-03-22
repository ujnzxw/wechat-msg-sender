# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
reload(sys)
sys.path.append('../')
sys.setdefaultencoding('utf-8')
import json
import codecs
import pymysql
from elasticsearch import Elasticsearch
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg


class ArticlePipeline(object):
    def __init__(self):
        self.__db_host       = xzcfg._get('database', 'host')
        self.__db_name       = xzcfg._get('database', 'bihu')
        self.__db_user       = xzcfg._get('database', 'bihu_user')
        self.__db_password   = xzcfg._get('database', 'bihu_password')
        self.__article_table = xzcfg._get('database', 'bihu_article_table')
        self.__article_not_found_table = xzcfg._get('database', 'bihu_article_not_found_table')

        self.__es = Elasticsearch()
        self.__db = pymysql.connect(
                host        = self.__db_host,
                user        = self.__db_user,
                passwd      = self.__db_password,
                db          = self.__db_name,
                charset     = "utf8",
                use_unicode = False
        )

    def process_item(self, item, spider):

        # data to db
        table = ''
        cursor = self.__db.cursor()

        # {"data":null,"res":100004,"resMsg":"保存失败"}
        # {"data":null,"res":100004,"resMsg":""}
        if item['title'] == '文章已删除或不存在':
            sql = "INSERT IGNORE INTO %s (artid) VALUES (%s)" %(self.__article_not_found_table, item['artid'])
            table = self.__article_not_found_table
        else:
            sql = "REPLACE INTO %s (artid, title, username, userid, boardname, updatime, content, money, ups, downs) \
                            VALUES ('%s', '%s',  '%s',     '%s',   '%s',      '%s',     '%s',    '%s',  '%s','%s');" \
                            %(self.__article_table,
                                item['artid'],
                                item['title'].replace("'", "''"),
                                item['username'],
                                item['userid'],
                                item['boardname'],
                                item['updatime'],
                                item['content'].replace("'", "''"),
                                item['money'],
                                item['ups'],
                                item['downs'])
            table = self.__article_table
        try:
            cursor.execute(sql)
            self.__db.commit()
            cursor.close()
            xzlog.success('Insert/update article to DB success, artid[%s], title[%s], table[%s]' %(item['artid'], item['title'], table))
        except BaseException as e:
            xzlog.error("insert data to DB error, artid[%s], EX[%s]" % (item['artid'], e))
            self.__db.commit()
            cursor.close()

        # data to es
        # {"data":null,"res":100004,"resMsg":"保存失败"}
        if item['title'] != u'\u4fdd\u5b58\u5931\u8d25':
            try:
                self.__es.index(index   = self.__db_name,
                        doc_type = self.__article_table,
                        id       = item['artid'],
                        body     ={"artId"     : item['artid'],
                                   "title"     : item['title'],
                                   "userName"  : item['username'],
                                   "boardName" : item['boardname'],
                                   "updatime"  : item['updatime'],
                                   "content"   : item['content'],
                                   "money"     : item['money'],
                                   "ups"       : item['ups'],
                                   "downs"     : item['downs']})
                xzlog.success('Insert article to es success, artid[%s], title[%s]' %(item['artid'], item['title']))
            except BaseException as e:
                xzlog.error("insert data to ES error, artid[%s], EX[%s]" % (item['artid'], e))
        return item

    def spider_closed(self, spider):
        self.__db.close()

