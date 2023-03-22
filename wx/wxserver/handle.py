# -*- coding: utf-8 -*-
# filename: handle.py
import sys
sys.path.append('../../')
import hashlib
import web
import reply
import receive
import re
from esengine import EsEngine
from dbengine import DbEngine
import message
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg

class Handle(object):
    def __init__(self):
        pass

    def GET(self):
        try:
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce     = data.nonce
            echostr   = data.echostr
            token     = "frombihu24h"

            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            xzlog.info("handle/GET func: hashcode[%s], signature[%s] " % (hashcode, signature))
            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception, Argument:
            return Argument

    def POST(self):
        try:
            webData = web.data()
            xzlog.info("Handle Post webdata[%s]" % webData)
            msg = ''
            recMsg = receive.parse_xml(webData)
            toUser   = recMsg.FromUserName
            fromUser = recMsg.ToUserName

            # save recive message to DB
            de = DbEngine()
            de.save_rec_msg(recMsg)

            if isinstance(recMsg, receive.Msg):
                if recMsg.MsgType == 'text':
                    recv_content = recMsg.Content
                    msg = self.handle_txt_msg(recv_content)
                else:
                    msg = message.SEARCH_NO_TEXT_MSG
                    xzlog.info("暂且不处理非文本消息")

                content  = msg
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            if isinstance(recMsg, receive.EventMsg):
                if recMsg.Event == 'CLICK':
                    if recMsg.Eventkey == 'mpGuide':
                        content = u"编写中，尚未完成".encode('utf-8')
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                if recMsg.Event in ('subscribe', 'unsubscribe'):
                        content = self.handle_event_msg(recMsg.Event)
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()

            xzlog.info("暂且不处理")
            return reply.Msg().send()

        except Exception, Argment:
            xzlog.info("ERROR for POST, Argment[%s]" % Argment)

            # 遇到系统错误，为了防止返回"服务出现故障"给用户，
            # 这里立马返回自定义提示以减少不满度
            webData = web.data()
            recMsg = receive.parse_xml(webData)
            toUser   = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            content  = message.UPGRADE_INPROGRESS_MSG
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return replyMsg.send()
            #return Argment

    def handle_event_msg(self, event):
        msg = ''
        if event == 'subscribe':
            msg = message.SUBSCRIBE_WELCOME_MSG
        else:
            xzlog.diagnose("Do not support this envet[%s]" % event)
            return "success"
        return msg

    def handle_txt_msg(self, content):
        msg = ''
        content = content.strip()

        # help query
        if content == '?' or content == '？':
            msg = message.HELP_MSG
            msg = msg.strip()

        # personal info and rank query
        elif content.decode('utf8').endswith(message.MY_INFO_AND_RANK_SUFFIX.decode('utf8')):
            # 这里先将中文字符串转码为unicode再截取
            # 不然会产生中文截取乱码现象
            content  = content.decode('utf8')
            suffix   = message.MY_INFO_AND_RANK_SUFFIX.decode('utf8')
            username = content.rstrip(suffix).encode('utf8')
            db       = DbEngine()
            msg      = db.get_personal_info_and_rank(username)

        # article ups rank query
        elif content == message.ARTICLE_UPS_RANK_QUERY:
            db  = DbEngine()
            msg = db.get_max_ups_rank(number=10)

        # article count rank query
        elif content == message.ARTICLE_COUNT_RANK_QUERY:
            db  = DbEngine()
            msg = db.get_article_count_rank(number=10)

        # person ups rank query
        elif content == message.PERSON_UPS_RANK_QUERY:
            db  = DbEngine()
            msg = db.get_person_ups_rank(number=10)

        # revenue rank query
        elif content == message.PERSON_REVENUE_RANK_QUERY:
            db  = DbEngine()
            msg = db.get_person_revenue_rank(number=10)

        # search rank query
        elif content == message.SEARCH_KEYWORDS_RANK_QUERY:
            msg = message.DEV_INPROGRESS_MSG

        # author query
        elif content.startswith('作者'):
            content = re.sub('^作者[：|:|\+]*', '', content)
            if len(content) == 0:
                msg = message.USERNAME_ERROR_MSG
            else:
                ee = EsEngine()
                return_list = ee.es_search_by_name(name=content)
                msg = ee.sharpen_message(return_list)
                if msg is None or len(msg) == 0:
                    msg = message.SEARCH_RETURN_NULL_MSG

        # content query
        elif content.startswith('内容'):
            content = re.sub('^内容[：|:|\+]*', '', content)
            if len(content) == 0:
                msg = message.CONTENT_ERROR_MSG
            else:
                ee = EsEngine()
                return_list = ee.es_search_by_content(keyword=content)
                msg = ee.sharpen_message(return_list)
                if msg is None or len(msg) == 0:
                    msg = message.SEARCH_RETURN_NULL_MSG

        # title query
        elif content.startswith('标题'):
            content = re.sub('^标题[：|:|\+]*', '', content)
            if len(content) == 0:
                msg = message.TITLE_ERROR_MSG
            else:
                ee = EsEngine()
                return_list = ee.es_search_by_title(keyword=content)
                msg = ee.sharpen_message(return_list)
                if msg is None or len(msg) == 0:
                    msg = message.SEARCH_RETURN_NULL_MSG

        # content and title query
        else:
            ee = EsEngine()
            return_list = ee.es_search_by_keyword(keyword=content)
            msg = ee.sharpen_message(return_list)
            if msg is None or len(msg) == 0:
                msg = message.SEARCH_RETURN_NULL_MSG

        return msg
