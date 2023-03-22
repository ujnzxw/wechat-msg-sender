# -*- coding: utf-8 -*-

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


class Db2Es(object):
    def __init__(self):
        self.__db_host       = xzcfg._get('database', 'host')
        self.__db_name       = xzcfg._get('database', 'bihu')
        self.__db_user       = xzcfg._get('database', 'bihu_user')
        self.__db_password   = xzcfg._get('database', 'bihu_password')
        self.__article_table = xzcfg._get('database', 'bihu_article_table')
        self.__es = Elasticsearch()
        self.__db = pymysql.connect(
                host        = self.__db_host,
                user        = self.__db_user,
                passwd      = self.__db_password,
                db          = self.__db_name,
                charset     = "utf8",
                use_unicode = False
        )

    def process_item(self, artid):

        # data from db
        item = {
            'artid' : "",
            'title' : "",
            'username' : "",
            'userid' : "",
            'boardname' : "",
            'updatime' : "",
            'content' : "",
            'money' : "",
            'ups' : "",
            'downs' : ""}
        cursor = self.__db.cursor()

        querysql = 'select 1 from %s where artid = %s limit 1;' % (self.__article_table, artid)
        count = cursor.execute(querysql)
        if count == 0:
            with open('not_found_artid.txt', 'a') as f:
                f.write(str(artid)+'\n')
            xzlog.info('artid[%s] do not exist' % artid)
            return
        else:
            xzlog.info('start to sync artid[%s] ' % artid)

        sql = "SELECT * FROM %s WHERE artid = %s" % (self.__article_table, artid)
        try:
            cursor.execute(sql)
            (item['artid'],
            item['title'],
            item['username'],
            item['userid'],
            item['boardname'],
            item['updatime'],
            item['content'],
            item['money'],
            item['ups'],
            item['downs']) = cursor.fetchone()
            self.__db.commit()
            cursor.close()
            xzlog.success('Read article from db success, artid=%s, title=%s' %(item['artid'], item['title']))
        except BaseException as e:
            xzlog.error(e)
            self.__db.commit()
            cursor.close()

        # data to es
        try:
            self.__es.index(index = self.__db_name,
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
            xzlog.success('Insert article to es success, artid=%s, title=%s' %(item['artid'], item['title']))
        except BaseException as e:
            xzlog.error("insert data to es error, artid[%s], EX[%s]" % (item['artid'], e))

if __name__ == '__main__':
    sync = Db2Es()
    for artid in range(150000, 170000):
        sync.process_item(artid)

