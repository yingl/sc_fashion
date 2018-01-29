# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import entry_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class EntryDgSpider(scrapy.Spider):
    name = 'entry_dg'
    allowed_domains = ['www.dolcegabbana.com.cn']

    def start_requests(self):
        database.init_database(config.db)
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            meta = job
            meta['config'] = config
            meta['database'] = database
            meta['parse'] = self.parse_page
            if utils.check_domain(url, EntryDgSpider.allowed_domains):
                yield scrapy.Request(url, callback=utils.parse, dont_filter=True, meta=meta)

    def parse_page(self, driver, url):
        products = []
        product_count = 0
        while True:
            elements = utils.find_elements_by_css_selector(driver, 'div.l-product_tiles > div.js-product_tile > div > a.js-producttile_link')
            if len(elements) > product_count:
                product_count = len(elements)
                driver.execute_script('window.scrollBy(0, document.body.scrollHeight);')
                utils.sleep(1)
            else:
                break
        for element in elements:
            products.append(element.get_attribute('href').strip())
        return ';'.join(products)