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

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        super(FourcljSpider, self).__init__()

    @classmethod
    def from_crawler(cls, crawler):
        user = crawler.settings["FOURCLJ_USER"]
        pwd = crawler.settings["FOURCLJ_PWD"]
        return cls(user, pwd)

    def start_requests(self):
        return [scrapy.FormRequest("http://www.4clojure.com/login", 
                                    formdata={ "user": self.user, "pwd": self.pwd }, callback=self.login)]

    def login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        for tr in response.css("#problem-table > tr"):
            link = response.urljoin(extract_first(tr.xpath("td[1]/a/@href")))
            title = extract_first(tr.xpath("td[1]/a/text()"))
            difficulty = extract_first(tr.xpath("td[2]/text()"))
            topics = extract_first(tr.xpath("td[3]/span/text()"))
            author = extract_first(tr.xpath("td[4]/text()"))
            nsolved = extract_first(tr.xpath("td[5]/text()"))
            issolved = extract_first(tr.xpath("td[6]/img[@alt='completed']"))
            yield ForclojureItem({
                "title": title,
                "link": link,
                "difficulty": difficulty,
                "topics": topics,
                "author": author,
                "nsolved": nsolved,
                "issolved": issolved
            })