# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import scrapy
import re
from forclojure.items import ForclojureItem, RestrictionItem

def extract_first(sel):
    if sel: return sel.extract_first()
    else: return ""

class RestrictionSpider(scrapy.Spider):
    name = "restrictionSpider"
    start_urls = ["http://www.4clojure.com/problems"]

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.pidre = re.compile(r"\d+$")
        super(RestrictionSpider, self).__init__()

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
            pid = self.pidre.findall(link)[0]
            yield scrapy.Request(link, callback=self.parseDetail, meta={"item": {"link": link, "title": title, "pid": pid}})

    def parseDetail(self, response):
        item = response.meta["item"]
        r = response.css("#restrictions > li::text")
        if r:
            item["restrictions"] = r.extract()
            yield RestrictionItem(item)