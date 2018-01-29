# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import entry_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class EntryStuartweitzmanSpider(scrapy.Spider):
    name = 'entry_stuartweitzman'
    allowed_domains = ['www.stuartweitzman.cn']
    start_urls = ['http://www.stuartweitzman.cn/']

    def start_requests(self):
        database.init_database(config.db)
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            meta = job
            meta['config'] = config
            meta['database'] = database
            meta['parse'] = self.parse_page
            if utils.check_domain(url, EntryStuartweitzmanSpider.allowed_domains):
                yield scrapy.Request(url, callback=utils.parse, dont_filter=True, meta=meta)
    def parse(self, response, url):
        driver = response.driver
        meta = response.meta
        result = utils.parse(driver, self.parse_page, meta, config)
        result['database'] = database # 传递db信息
        yield result

    def parse_page(self, driver, url):
        products = []
        elements = utils.find_elements_by_css_selector(driver, 'div.productgridItem > ul.prod_style > li[style="display:block"]  > div.prod_grid > a')
        for element in elements:
            products.append(element.get_attribute('href').strip())
        return ';'.join(products)
