# -*- coding: utf-8 -*-
'''
elasticsearch engine
'''

import sys
import urllib
import copy
reload(sys)
sys.path.append('../../')
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg
from elasticsearch import Elasticsearch
from string import Template
import message


class EsEngine(object):
    ARTICLE_RTN = {
                "title"    : "",
                "username" : "",
                "artid"    : ""
                }

    def __init__(self):
        self.__db_name       = xzcfg._get('database', 'bihu')
        self.__article_table = xzcfg._get('database', 'bihu_article_table')
        self.__es = Elasticsearch()

    def es_insert(self, index, doc_type, id, body):
        try:
            self.__es.index(index, doc_type, id, body)
            xzlog.success('insert to ES: index[%s], doc_type[%s], id[%s]' % (index, doc_type, id))
        except BaseException as e:
            xzlog.error('insert to ES: index[%s], doc_type[%s], id[%s], EX[%s]' % (index, doc_type, id, e))

    def es_search(self, index, doc_type, body):
        try:
            res = self.__es.search(index, doc_type, body)
            return res
        except BaseException as e:
            xzlog.error('search from ES: index[%s], doc_type[%s], body[%s], EX[%s]' % (index, doc_type, body, e))

    """
    search keyword in userName
    """
    def es_search_by_name(self, name="东湾", index='bihu', doc_type='article'):
        body = {
            "query":{
                "match":{
                    "userName":name
                }
            }
        }
        res = self.es_search(index, doc_type, body)
        return self.extract_msg(res)

    """
    search keyword in title and content and name
    """
    def es_search_by_keyword(self, keyword="头条", index='bihu', doc_type='article'):
        body = {
            "query":{
                "multi_match":{
                    "query":keyword,
                    "fields":["title", "content", "userName"]
                }
            }
        }
        res = self.es_search(index, doc_type, body)
        return self.extract_msg(res)
    """
    search keyword in content
    """
    def es_search_by_content(self, keyword="头条", index='bihu', doc_type='article'):
        body = {
            "query":{
                "match":{
                    "content":keyword
                }
            }
        }
        res = self.es_search(index, doc_type, body)
        return self.extract_msg(res)

    """
    search keyword in title
    """
    def es_search_by_title(self, keyword="头条", index='bihu', doc_type='article'):
        body = {
            "query":{
                "match":{
                    "title":keyword
                }
            }
        }
        res = self.es_search(index, doc_type, body)
        return self.extract_msg(res)

    """
    extract message from ES returned dictionary
    """
    def extract_msg(self,res):
        return_list = []
        for item in res['hits']['hits']:
            rt = copy.deepcopy(self.ARTICLE_RTN)
            rt["title"]    = self.to_utf8(item['_source']['title'])
            if rt["title"] is None or rt["title"] == '':
                rt["title"] = message.NO_ARTICLE_TITLE
            rt["username"] = self.to_utf8(item['_source']['userName'])
            rt["artid"]    = self.to_utf8(item['_source']['artId'])
            return_list.append(rt)
        return return_list

    def to_utf8(self, mystr):
        if isinstance(mystr, unicode):
            return urllib.unquote(mystr).encode('utf-8')
        elif isinstance(mystr, str):
            return urllib.unquote(mystr)
        elif isinstance(mystr, int):
            return urllib.unquote(str(mystr))

        else:
            return mystr
        #else:
        #    raise xzlog.error('unkonwn string type')
    def sharpen_message(self, item_list):
        msg = ''
        template_str = message.SEARCH_RETURN_MSG_TEMPLATE
        t = Template(template_str)
        for item in item_list:
            msg = msg + t.substitute(title=item['title'], artid=item['artid'], username=item['username'])
        return msg



if __name__ == "__main__":
    ee = EsEngine()
    #rtn =  ee.es_search_by_name(name="糖果")
    rtn =  ee.es_search_by_keyword(keyword="社区")
    msg = ee.sharpen_message(rtn)
    print msg
