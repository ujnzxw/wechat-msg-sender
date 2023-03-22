# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    artid    = scrapy.Field()
    title    = scrapy.Field()
    boardname= scrapy.Field()
    username = scrapy.Field()
    userid   = scrapy.Field()
    updatime = scrapy.Field()
    content  = scrapy.Field()
    money    = scrapy.Field()
    ups      = scrapy.Field()
    downs    = scrapy.Field()

class ProxyItem(scrapy.Item):
    ip       = scrapy.Field()
    port     = scrapy.Field()
    iptype   = scrapy.Field()
    speed    = scrapy.Field()
