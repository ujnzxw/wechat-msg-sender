# -*- coding: utf-8 -*-
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import json
import urllib2
from utils.wxtoken import AccessToken

class CreateMenu(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.data = self.get_data()

    def create_menu(self):
        t = AccessToken()
        access_token = t.get_access_token()
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % access_token
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('encoding', 'utf-8')
        response = urllib2.urlopen(req, json.dumps(self.data,ensure_ascii=False))
        result = response.read()
        print result

    def get_data(self):
        data = {}
        f = open(self.config_file, 'rb')
        data = json.load(f)
        f.close()
        return data
if __name__ == '__main__':
    cm = CreateMenu('../config/menu.json')
    cm.create_menu()

