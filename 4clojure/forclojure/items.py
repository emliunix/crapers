# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

def topicSerializer(val):
    return [v for v in str(val).split(" ") if v != ""]

class ForclojureItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    link = Field()
    difficulty = Field()
    topics = Field(serializer=topicSerializer)
    author = Field()
    nsolved = Field(serializer=int)
