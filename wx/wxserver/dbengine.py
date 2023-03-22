# -*- coding: utf-8 -*-
'''
Mariadb engine
'''

import sys
import urllib
import copy
reload(sys)
sys.path.append('../../')
import pymysql
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg
from elasticsearch import Elasticsearch
from string import Template
import receive
import message


class DbEngine(object):
    UPS_RANK_RTN = {
                "title"    : "",
                "username" : "",
                "artid"    : "",
                "ups"      : ""}

    ART_CNT_RANK_RTN = {
                    "username" : "",
                    "userid"   : "",
                    "count"    : ""}

    PERSON_UPS_RANK_RTN = {
                    "username"  : "",
                    "userid"    : "",
                    "total_ups" : ""}

    PERSON_REVENUE_RANK_RTN = {
                    "username"      : "",
                    "userid"        : "",
                    "total_revenue" : ""}

    MY_INFO_AND_RANK_RTN = {
                    "username"      : "",
                    "art_count"     : "", #发文量
                    "art_rank"      : "",
                    "ups_count"     : "", #收赞量
                    "ups_rank"      : "",
                    "rev_count"     : "", #收入
                    "rev_rank"      : ""}

    def __init__(self):
        self.__db_host       = xzcfg._get('database', 'host')
        self.__db_name       = xzcfg._get('database', 'bihu')
        self.__db_user       = xzcfg._get('database', 'bihu_user')
        self.__db_password   = xzcfg._get('database', 'bihu_password')
        self.__article_table = xzcfg._get('database', 'bihu_article_table')

    """
    Get max number ups rank from DB
    """
    def get_max_ups_rank(self, number=10):
        item_list = []
        db = pymysql.connect(
            host        = self.__db_host,
            user        = self.__db_user,
            passwd      = self.__db_password,
            db          = self.__db_name,
            charset     = "utf8",
            use_unicode = False)
        sql = "select title,username,artid,ups from %s order by CAST(ups as UNSIGNED INTEGER) desc limit %s;" \
            % (self.__article_table, number)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            items = cursor.fetchall()
            for item in items:
                rt = copy.deepcopy(self.UPS_RANK_RTN)
                (rt["title"], rt["username"], rt["artid"], rt["ups"]) = item
                if rt["title"] is None or rt["title"] == '':
                    rt["title"] = message.NO_ARTICLE_TITLE
                item_list.append(rt)
        except BaseException as e:
            xzlog.error("error in get ups rank, EX[%s]" % e)
        db.commit()
        cursor.close()
        db.close()
        return self.sharpen_max_ups_rank_msg(item_list)
    def get_article_count_rank(self, number=10):
        item_list = []
        db = pymysql.connect(
            host        = self.__db_host,
            user        = self.__db_user,
            passwd      = self.__db_password,
            db          = self.__db_name,
            charset     = "utf8",
            use_unicode = False)
        sql = "SELECT username,userid,count( * ) AS count FROM %s GROUP BY username ORDER BY count DESC LIMIT %s;" \
            % (self.__article_table, number)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            items = cursor.fetchall()
            for item in items:
                rt = copy.deepcopy(self.ART_CNT_RANK_RTN)
                (rt["username"], rt["userid"], rt["count"]) = item
                item_list.append(rt)
        except BaseException as e:
            xzlog.error("error in get ups rank, EX[%s]" % e)
        db.commit()
        cursor.close()
        db.close()
        return self.sharpen_article_count_rank_msg(item_list)
    def get_personal_info_and_rank(self, username="东湾以东"):
        item = copy.deepcopy(self.MY_INFO_AND_RANK_RTN)
        db = pymysql.connect(
            host        = self.__db_host,
            user        = self.__db_user,
            passwd      = self.__db_password,
            db          = self.__db_name,
            charset     = "utf8",
            use_unicode = False)
        chk_sql = "select 1 from %s where username='%s' limit 1;" % ( self.__article_table, username )

        art_sql = "SELECT T2.rowNo, T2.username, T2.art_number \
                   FROM \
                   (SELECT T1.art_number, \
                           T1.username, \
                           IF(@c=T1.art_number,@rowNo:=@rowNo,@rowNo:=@rowNo+1) AS rowNo, \
                           @c:=T1.art_number \
                   FROM \
                     ( \
                       SELECT username,COUNT(username) AS art_number \
                       FROM %s \
                       GROUP BY username \
                       ORDER BY art_number DESC \
                     )T1 \
                   )T2, (SELECT @c:=0,@rowNo:=0)T3 \
                   WHERE T2.username='%s'" % (self.__article_table, username)

        rev_sql = "SELECT T2.rowNo, T2.username, T2.total_revenue                     \
                   FROM                                                               \
                   (SELECT T1.total_revenue,                                          \
                           T1.username,                                               \
                           IF(@c=T1.total_revenue,@rowNo:=@rowNo,@rowNo:=@rowNo+1) AS rowNo, \
                           @c:=T1.total_revenue                                       \
                   FROM                                                               \
                     (                                                                \
                       SELECT username,SUM(money) AS total_revenue                    \
                       FROM %s                                                        \
                       GROUP BY username                                              \
                       ORDER BY total_revenue DESC                                    \
                     )T1                                                              \
                   )T2, (SELECT @rowNo:=0,@c:=0)T3                                    \
                   WHERE username='%s';"                                              \
                   % (self.__article_table, username)

        ups_sql = "SELECT T2.rowNo, T2.username, T2.total_ups                         \
                   FROM                                                               \
                   (SELECT T1.total_ups,                                              \
                           T1.username,                                               \
                           IF(@c=T1.total_ups,@rowNo:=@rowNo,@rowNo:=@rowNo+1) AS rowNo, \
                           @c:=T1.total_ups                                           \
                   FROM                                                               \
                     (                                                                \
                       SELECT username,SUM(ups) AS total_ups                          \
                       FROM %s                                                        \
                       GROUP BY username                                              \
                       ORDER BY total_ups DESC                                        \
                     )T1                                                              \
                   )T2, (SELECT @rowNo:=0,@c:=0)T3                                    \
                   WHERE username='%s';"                                              \
                   % (self.__article_table, username)
        try:
            cursor = db.cursor()
            effect_row = cursor.execute(chk_sql)
            cursor.close()
            if effect_row == 0:
                db.close()
                return message.MY_INFO_AND_RANK_ERROR
            cursor1 = db.cursor()
            # TODO 这个地方执行两遍
            # 执行第一遍总是无法解决相同分数的情况下名次也应相同的问题。
            # 执行第二遍就解决了，不知道为什么
            cursor1.execute(art_sql)
            cursor1.execute(art_sql)
            (item["art_rank"],item["username"],item["art_number"]) = cursor1.fetchone()
            cursor1.close()

            cursor2 = db.cursor()
            cursor2.execute(ups_sql)
            (item["ups_rank"],item["username"],item["ups_number"]) = cursor2.fetchone()
            cursor2.close()

            cursor3 = db.cursor()
            cursor3.execute(rev_sql)
            (item["rev_rank"],item["username"],item["rev_number"]) = cursor3.fetchone()
            cursor3.close()

        except BaseException as e:
            xzlog.error("error in get personal info and rank, EX[%s]" % e)
        db.commit()
        cursor.close()
        db.close()
        return self.sharpen_personal_info_and_rank_msg(item)
    """
    Get max number ups rank from DB
    """
    def get_person_ups_rank(self, number=10):
        item_list = []
        db = pymysql.connect(
            host        = self.__db_host,
            user        = self.__db_user,
            passwd      = self.__db_password,
            db          = self.__db_name,
            charset     = "utf8",
            use_unicode = False)
        sql = "SELECT username,userid,sum(ups) AS total_ups FROM %s group by username ORDER BY total_ups DESC LIMIT %s;" \
            % (self.__article_table, number)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            items = cursor.fetchall()
            for item in items:
                rt = copy.deepcopy(self.PERSON_UPS_RANK_RTN)
                (rt["username"], rt["userid"], rt["total_ups"]) = item
                item_list.append(rt)
        except BaseException as e:
            xzlog.error("error in get ups rank, EX[%s]" % e)
        db.commit()
        cursor.close()
        db.close()
        return self.sharpen_person_ups_rank_msg(item_list)

    """
    Get max number ups rank from DB
    """
    def get_person_revenue_rank(self, number=10):
        item_list = []
        db = pymysql.connect(
            host        = self.__db_host,
            user        = self.__db_user,
            passwd      = self.__db_password,
            db          = self.__db_name,
            charset     = "utf8",
            use_unicode = False)
        sql = "SELECT username,userid,sum(money) AS total_revenue FROM %s group by username ORDER BY total_revenue DESC LIMIT %s;" \
            % (self.__article_table, number)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            items = cursor.fetchall()
            for item in items:
                rt = copy.deepcopy(self.PERSON_REVENUE_RANK_RTN)
                (rt["username"], rt["userid"], rt["total_revenue"]) = item
                item_list.append(rt)
        except BaseException as e:
            xzlog.error("error in get ups rank, EX[%s]" % e)
        db.commit()
        cursor.close()
        db.close()
        return self.sharpen_person_revenue_rank_msg(item_list)

    """
    Save received msg to DB
    """
    def save_rec_msg(self, recMsg):
        db = pymysql.connect(
            host        = self.__db_host,
            user        = xzcfg._get('database', 'wx_user'),
            passwd      = xzcfg._get('database', 'wx_password'),
            db          = xzcfg._get('database', 'wx'),
            charset     = "utf8",
            use_unicode = False)
        table = xzcfg._get('database', 'wx_msg_table')
        if isinstance(recMsg, receive.Msg):
            if recMsg.MsgType == 'text':
                cursor = db.cursor()
                sql = "INSERT INTO %s (MsgId, ToUserName, FromUserName, CreateTime, MsgType, Content) \
                               VALUES ('%s',  '%s',       '%s',         '%s',       '%s',    '%s');"  \
                    % (table,               \
                       recMsg.MsgId,        \
                       recMsg.ToUserName,   \
                       recMsg.FromUserName, \
                       recMsg.CreateTime,   \
                       recMsg.MsgType,      \
                       recMsg.Content)
                try:
                    cursor.execute(sql)
                except BaseException as e:
                    xzlog.error("error in save message, EX[%s]" % e)
                db.commit()
                cursor.close()
            else:
                xzlog.info("暂且不保存非文本消息")
        if isinstance(recMsg, receive.EventMsg):
            xzlog.info("暂且不处理事件消息")

        db.close()
        return True

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
        return msg.strip()
    def sharpen_max_ups_rank_msg(self, item_list):
        msg = ''
        template_header = message.ARTICLE_UPS_RANK_MSG_TEMPLATE_HEADER
        th = Template(template_header)
        header = th.substitute(total=len(item_list))

        template_str = message.ARTICLE_UPS_RANK_MSG_TEMPLATE
        t = Template(template_str)
        for i, item in enumerate(item_list):
            msg = msg + t.substitute(number = i+1, title=item['title'], artid=item['artid'], ups=item['ups'])

        msg = header + msg
        return msg.strip()

    def sharpen_article_count_rank_msg(self, item_list):
        msg = ''
        template_header = message.ARTICLE_COUNT_RANK_MSG_TEMPLATE_HEADER
        th = Template(template_header)
        header = th.substitute(total=len(item_list))

        template_str    = message.ARTICLE_COUNT_RANK_MSG_TEMPLATE
        t = Template(template_str)
        for i, item in enumerate(item_list):
            msg = msg + t.substitute(number = i+1, username=item['username'], userid=item['userid'], count=item['count'])

        msg = header + msg
        return msg.strip()

    def sharpen_person_ups_rank_msg(self, item_list):
        msg = ''
        template_header = message.PERSON_UPS_RANK_MSG_TEMPLATE_HEADER
        th = Template(template_header)
        header = th.substitute(total=len(item_list))
        template_str    = message.PERSON_UPS_RANK_MSG_TEMPLATE
        t = Template(template_str)
        for i, item in enumerate(item_list):
            msg = msg + t.substitute(number = i+1, username=item['username'], userid=item['userid'], total_ups=str(int(item['total_ups'])))

        msg = header + msg
        return msg.strip()

    def sharpen_person_revenue_rank_msg(self, item_list):
        msg = ''
        template_header = message.PERSON_REVENUE_RANK_MSG_TEMPLATE_HEADER
        th = Template(template_header)
        header = th.substitute(total=len(item_list))
        template_str    = message.PERSON_REVENUE_RANK_MSG_TEMPLATE
        t = Template(template_str)
        for i, item in enumerate(item_list):
            msg = msg + t.substitute(number = i+1, username=item['username'], userid=item['userid'], total_revenue=str(item['total_revenue']))

        msg = header + msg
        return msg.strip()
    def sharpen_personal_info_and_rank_msg(self, item):
        msg = ''
        template_str    = message.MY_INFO_AND_RANK_TEMPLATE
        t = Template(template_str)
        msg = t.substitute(username=item['username'],               \
                           art_number=str(int(item['art_number'])), \
                           art_rank=str(int(item['art_rank'])),     \
                           ups_number=str(int(item['ups_number'])), \
                           ups_rank=str(int(item['ups_rank'])),     \
                           rev_number=item['rev_number'],           \
                           rev_rank=str(int(item['rev_rank'])))
        return msg.strip()


if __name__ == "__main__":
    mdb = DbEngine()
    mdb.get_max_ups_rank()
