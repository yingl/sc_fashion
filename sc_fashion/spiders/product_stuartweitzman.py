# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import product_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class ProductStuartweitzmanSpider(scrapy.Spider):
    name = 'product_stuartweitzman'
    brand = 'stuartweitzman'
    allowed_domains = ['www.stuartweitzman.cn']

    def __init__(self):
        database.init_database(config.db)

    def start_requests(self):
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            if utils.check_domain(url, ProductStuartweitzmanSpider.allowed_domains):
                yield scrapy.Request('http://localhost', callback=self.parse, dont_filter=True, meta=job)

    def parse(self, response):
        result = utils.parse(self.parse_page, response.meta, config)
        result['database'] = database # 传递db信息
        yield result

    def parse_page(self, driver, url):
        products = []
        driver.get(url)
        product = {'brand': ProductStuartweitzmanSpider.brand,
                   'code': '',
                   'price': 0,
                   'images': '',
                   'detail': ''}
        # check 404
        element = utils.find_element_by_css_selector(driver, 'div.information_message.negative > p')
        if element:
            if element.text.strip() == '404 页面未找到':
                raise Exception('404 page not found')
        # title
        element = utils.find_element_by_css_selector(driver, 'h1.pdname > span')
        if element:
            product['title'] = element.text.strip()
        else:
            raise Exception('Title not found for %s' % driver.current_url)
        # code/NA
        # unit
        product['unit'] = config.rmb
        # price
        element = utils.find_element_by_css_selector(driver, 'p.big-price')
        if element:
            price_text = element.text.strip()
            # 打折的情况需要处理
            if '|' in price_text: # 打折
                price_text = price_text.split('|')[1].strip().split(' ')[0][1:]
            else:
                price_text = price_text[1:-2].strip()
            price_text = price_text.replace(',', '')
            product['price'] = float(price_text)
        # images
        elements = utils.find_elements_by_css_selector(driver, 'ul#carousel_alternate > li > span > a > img')
        images = [element.get_attribute('data-primaryimagesrc').strip() for element in elements]
        product['images'] = ';'.join(images)
        # detail
        element = utils.find_element_by_css_selector(driver, 'div.pdp-description')
        if element:
            product['detail'] = element.text.strip()
        return product
