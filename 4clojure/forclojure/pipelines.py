# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import forclojure.items

dbconfig = {
    "user": "liu",
    "database": "liu",
    "password": "liu.p",
    "host": "localhost",
    "port": 5432
}

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
        nsolved INT DEFAULT 0
    )""")

def serializeItem(item):
    data = {}
    for (field_name, field) in item.fields.items():
        serializefn = field.get("serializer", lambda x: x)
        data[field_name] = serializefn(item[field_name])
    return data

class DBPipeline(object):
    def __init__(self):
        self.q = []
        self.throttle = 20
        self.conn = None

    def push(self, item):
        item_seria = serializeItem(item)
        data = [item_seria[x] for x in ["title", "link", "difficulty", "topics", "author", "nsolved"]]
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
                INSERT INTO fourcljproblems (title, link, difficulty, topics, author, nsolved)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, vals)
            self.conn.commit()
        except psycopg2.DatabaseError as err:
            self.q = vals
            self.conn.rollback()
            print(err)

    def open_spider(self, spider):
        self.conn = psycopg2.connect(**dbconfig)
        initdb(self.conn.cursor())
        self.conn.commit()
    
    def close_spider(self, spider):
        self.batchprocess()
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, forclojure.items.ForclojureItem):
            self.push(item)
        return item
