# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import entry_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class EntryLoeweSpider(scrapy.Spider):
    name = 'entry_loewe'
    allowed_domains = ['www.loewe.com']
    start_urls = ['http://www.loewe.com/']

    def __init__(self):
        database.init_database(config.db)

    def start_requests(self):
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            if utils.check_domain(url, EntryLoeweSpider.allowed_domains):
                # 利用http://localhost降低请求成本，把需要selenium处理的url通过meta传递。
                yield scrapy.Request('http://localhost', callback=self.parse, dont_filter=True, meta=job)

    def parse(self, response):
        result = utils.parse(self.parse_page, response.meta, config)
        result['database'] = database # 传递db信息
        yield result

    def parse_page(self, driver, url):
        driver.get(url)
        # 点击展开分页
        element = utils.find_element_by_css_selector(driver, 'li.view-all-products > span')
        if element:
            driver.execute_script('arguments[0].click();', element)
        # 下拉刷新
        products = []
        product_count = 0
        while True:
            elements = utils.find_elements_by_css_selector(driver, 'div.product-tile > figure > a.thumb-link')
            if len(elements) > product_count:
                product_count = len(elements)
                driver.execute_script('window.scrollBy(0, document.body.scrollHeight);')
                utils.sleep(1)
            else:
                break
        for element in elements:
            products.append(element.get_attribute('href').strip())
        return ';'.join(products)
