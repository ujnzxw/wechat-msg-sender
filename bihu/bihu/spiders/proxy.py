# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
print sys.path
import scrapy
from bihu.items import ProxyItem
from lib.xzlog import xzlog
from lib.xzcfg import xzcfg


class ArticleSpider(scrapy.Spider):
    name = 'proxy'
    def __init__(self, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)

        self.start_urls = ['http://www.xicidaili.com/nn/']

    def parse(self, response):
        #print response.body
            #print sel.body
            for i in range(2, 5):
                item = ProxyItem()
                item['ip']    = response.xpath('//table/tbody/tr[%s]/td[2]' % str(i)).extract()
                print 'zxw' + '/html/body/div[1]/div[2]/table/tbody/tr[%s]/td[2]' % str(i)
                item['port']  = response.xpath('/html/body/div[1]/div[2]/table/tbody/tr[%s]/td[3]/text()' % str(i)).extract_first()
                item['iptype']= response.xpath('/html/body/div[1]/div[2]/table/tbody/tr[%s]/td[6]/text()' % str(i)).extract_first()
                item['speed'] = response.xpath('/html/body/div[1]/div[2]/table/tbody/tr[%s]/td[8]/div/@title' % str(i)).extract_first()
                xzlog.info("zxw ip[%s],speed[%s]" %(item['ip'], item['speed']))
                yield item

