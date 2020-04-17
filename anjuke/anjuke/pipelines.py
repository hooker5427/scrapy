# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class AnjukePipeline(object):

    def  __init__(self):
        self.file =  open('price.csv' ,"ab")


    def __del__(self):
        self.file.close()


    def process_item(self, item, spider):

        self.file.write( (str(item) + "\r\n").encode("utf-8" ,'ignore'))
        self.file.flush()
        return item
