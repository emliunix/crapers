# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import forclojure.items
import logging

logger = logging.getLogger("PGPipeline")

def initdb(cur):
    """
    :param cur: cursor
    """
    cur.execute("""CREATE TABLE IF NOT EXISTS fourcljproblems (
        pid SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        link VARCHAR(200) NOT NULL,
        difficulty VARCHAR(20) NOT NULL,
        topics VARCHAR(100)[] DEFAULT '{}',
        author VARCHAR(100) NOT NULL,
        nsolved INT DEFAULT 0,
        issolved BOOLEAN DEFAULT FALSE
    )""")

def serializeItem(item):
    data = {}
    for (field_name, field) in item.fields.items():
        serializefn = field.get("serializer", lambda x: x)
        data[field_name] = serializefn(item[field_name])
    return data

class DBPipeline(object):
    def __init__(self, config):
        self.config = config
        self.q = []
        self.throttle = 20
        self.conn = None
        self.noop = False

    def push(self, item):
        item_seria = serializeItem(item)
        data = [item_seria[x] for x in ["title", "link", "difficulty", "topics", "author", "nsolved", "issolved"]]
        self.q.append(data)
        if len(self.q) >= self.throttle:
            self.batchprocess()

    def batchprocess(self):
        try:
            with self.conn.cursor() as cur:
                # isolate data
                vals = self.q
                self.q = []

                cur.executemany("""
                INSERT INTO fourcljproblems (title, link, difficulty, topics, author, nsolved, issolved)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, vals)
            self.conn.commit()
        except psycopg2.DatabaseError as err:
            self.q = vals
            self.conn.rollback()
            logger.warn("Batch Processing Failed. Data not saved to db.")
            logger.warn(err)

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings["FOURCLJ_SAVE_TO_PG"]:
            logger.info("Data will be saved to pg.")
            return cls(crawler.settings["FOURCLJ_PG_CONFIG"])
        else:
            logger.info("Data will not be saved to pg.")
            return NoopPipeline()

    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(**self.config)
        except psycopg2.DatabaseError as err:
            # so something goes wrong, make this behave like NoopPipeline
            logger.error("Error connect to db")
            self.noop = True
            # self.process_item = NoopPipeline.process_item
            # del(self.close_spider)
        else: # if everything is ok
            initdb(self.conn.cursor())
            self.conn.commit()
    
    def close_spider(self, spider):
        if not self.noop:
            self.batchprocess()
            self.conn.close()

    #pylint: disable=E0202
    def process_item(self, item, spider):
        if not self.noop and isinstance(item, forclojure.items.ForclojureItem):
            self.push(item)
        return item

class NoopPipeline(object):
    def process_item(self, item, spider):
        return item