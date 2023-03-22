#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,urllib2,json
import sys;reload(sys)
sys.path.append('../../')

import MySQLdb
import time

from optparse import OptionParser
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg
sys.setdefaultencoding( "utf-8" )
def Singleton(cls):
    _instance = {}
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    return _singleton

@Singleton
class AccessToken(object):
    __token_id = ''
    # Init attribute
    def __init__(self):
        self.__url         = xzcfg._get('server', 'url').rstrip('/')
        self.__appid       = xzcfg._get('server', 'appid')
        self.__secret      = xzcfg._get('server', 'secret')

        self.__db_host     = xzcfg._get('database', 'host')
        self.__db_name     = xzcfg._get('database', 'wx')
        self.__db_user     = xzcfg._get('database', 'wx_user')
        self.__db_password = xzcfg._get('database', 'wx_password')
        self.__token_table = xzcfg._get('database', 'wx_token_table')

    """
    @Summary   : get token id
    @Parameter : url_prefix='/'
    @Attention : the token will fill into self.__token_id
    """
    def __real_get_token(self, url_prefix='/'):
        content = {}
        params  = {
                    'grant_type' : 'client_credential',
                    'appid'      : self.__appid,
                    'secret'     : self.__secret
                  }

        data     = urllib.urlencode(params)
        url      = self.__url + url_prefix + 'token?'
        response = urllib.urlopen(url, data)
        content  = json.loads(response.read())

        try:
            access_token = content['access_token']
            expires_in   = content['expires_in']
        except KeyError:
            xzlog.error("get access token from wechat server error!")
            raise KeyError
        return (access_token,expires_in)
    def get_access_token(self):
        '''
        access_token | expires_in | update_time
        '''
        access_token = ''
        expires_in = 0
        update_time = 0
        return_token = ''
        timestamp = str(int(time.time()))
        db = MySQLdb.connect(
                            host=self.__db_host,
                            user=self.__db_user,
                            passwd=self.__db_password,
                            db=self.__db_name)

        # use cursor() to get cursor
        cursor = db.cursor()

        sql = 'SELECT * FROM %s' % self.__token_table
        try:
            count = cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        # access token existed
        if count > 0:

            if count > 1 :
                xzlog.error("access token record count bigger than 1")
                db.close()

            (access_token, expires_in, update_time) = cursor.fetchone()

            # expired
            new_access_token = ''
            new_expires_in   = 0

            if int(update_time) + int(expires_in) < int(timestamp):
                (new_access_token, new_expires_in) = self.__real_get_token()

                update_sql = "UPDATE %s SET      \
                            access_token=\'%s\', \
                            expires_in=\'%s\',   \
                            update_time=\'%s\'   \
                            WHERE access_token=\'%s\';" \
                            % (self.__token_table, new_access_token, new_expires_in, timestamp, access_token)
                try:
                    cursor.execute(update_sql)
                    db.commit()
                except:
                    db.rollback()

                return_token = new_access_token
            # not expired
            else:
                return_token = access_token

        # access token not existed
        else:
            (new_access_token, new_expires_in) = self.__real_get_token()
            insert_sql = "INSERT INTO %s (access_token, expires_in, update_time) \
                        VALUES ('%s', '%s', '%s')" \
                        % (self.__token_table, new_access_token, new_expires_in, timestamp)
            try:
                cursor.execute(insert_sql)
                db.commit()
            except:
                db.rollback()

            return_token = new_access_token

        db.close()

        return return_token



if __name__ == '__main__':
        t = AccessToken()
        access_token = t.get_access_token()
        print access_token
