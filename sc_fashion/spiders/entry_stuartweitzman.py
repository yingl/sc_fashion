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

    def __init__(self):
        database.init_database(config.db)

    def start_requests(self):
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            if utils.check_domain(url, EntryStuartweitzmanSpider.allowed_domains):
                yield scrapy.Request('http://localhost', callback=self.parse, dont_filter=True, meta=job)

    def parse(self, response):
        result = utils.parse(self.parse_page, response.meta, config)
        result['database'] = database # 传递db信息
        yield result

    def parse_page(self, driver, url):
        products = []
        driver.get(url)
        elements = utils.find_elements_by_css_selector(driver, 'div.productgridItem > ul.prod_style > li[style="display:block"]  > div.prod_grid > a')
        for element in elements:
            products.append(element.get_attribute('href').strip())
        return ';'.join(products)
