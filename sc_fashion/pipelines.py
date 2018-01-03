# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

class EntryProductPipeline(object):
    def process_item(self, item, spider):
        if not (spider.name.startswith('entry_') or \
                spider.name.startswith('product_')):
            return item
        database = item['database']
        content = item['content']
        if content:
            result = database.Result.select(). \
                                     where(database.Result.source_id == item['source_id'])
            if result: # 更新记录
                result = result.get()
                result.updated_at = datetime.now()
            else:
                result = database.Result()
                result.source_id = item['source_id']
            result.content = content
            result.save()
        job = database.Job.select(). \
                           where(database.Job.id == item['job_id']).get()
        job.status = item['status']
        job.message = item['message']
        job.updated_at = datetime.now()
        job.save()
