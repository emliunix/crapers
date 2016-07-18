# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import scrapy
from forclojure.items import ForclojureItem

def extract_first(sel):
    if sel: return sel.extract_first()
    else: return ""

class FourcljSpider(scrapy.Spider):
    name = "4cljSpider"
    start_urls = ["http://www.4clojure.com/problems"]

    def parse(self, response):
        for tr in response.css("#problem-table > tr"):
            link = response.urljoin(extract_first(tr.xpath("td[1]/a/@href")))
            title = extract_first(tr.xpath("td[1]/a/text()"))
            difficulty = extract_first(tr.xpath("td[2]/text()"))
            topics = extract_first(tr.xpath("td[3]/span/text()"))
            author = extract_first(tr.xpath("td[4]/text()"))
            nsolved = extract_first(tr.xpath("td[5]/text()"))
            yield ForclojureItem({
                "title": title,
                "link": link,
                "difficulty": difficulty,
                "topics": topics,
                "author": author,
                "nsolved": nsolved
            })