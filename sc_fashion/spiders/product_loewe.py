# -*- coding: utf-8 -*-
import re
import scrapy
import traceback
from sc_fashion.extras import product_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class ProductLoeweSpider(scrapy.Spider):
    name = 'product_lowew'
    brand = 'loewe'
    allowed_domains = ['www.loewe.com']

    def start_requests(self):
        database.init_database(config.db)
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            meta = job
            meta['config'] = config
            meta['database'] = database
            meta['parse'] = self.parse_page
            if utils.check_domain(url, ProductLoeweSpider.allowed_domains):
                yield scrapy.Request(url, callback=utils.parse, dont_filter=True, meta=meta)

    def parse_page(self, driver, url):
        products = []
        product = {'url': url,
                   'brand': ProductLoeweSpider.brand,
                   'code': '',
                   'price': 0,
                   'images': '',
                   'detail': ''}
        # 切换语言
        element = utils.find_element_by_css_selector(driver, 'div.siteSelectors-current.siteSelectors-current-locale')
        if element:
            driver.execute_script('arguments[0].click();', element)
            utils.sleep(1)
            elements = utils.find_elements_by_css_selector(driver, 'ul.siteSelectors-list-locale[data-country=CN] > li > a')
            switch_to_chinese = False
            for element in elements:
                if element.get_attribute('innerHTML').strip() == 'Simplified Chinese':
                    driver.execute_script('arguments[0].click();', element)
                    utils.sleep(1)
                    switch_to_chinese = True
                    break
            if not switch_to_chinese:
                raise Exception("Can't switch to Chinese")
        else:
            raise Exception("Cant't select language")
        # check 404
        element = utils.find_element_by_css_selector(driver, 'div.error404')
        if element:
            raise Exception('404 page not found')
        # title
        element = utils.find_element_by_css_selector(driver, 'h1.product-name')
        if element:
            product['title'] = element.text.strip()
        else:
            raise Exception('Title not found for %s' % driver.current_url)
        # code
        element = utils.find_element_by_css_selector(driver, 'span.model-id')
        if element:
            product['code'] = element.text.strip().split(': ')[1]
        # unit
        product['unit'] = config.rmb
        # price
        element = utils.find_element_by_css_selector(driver, 'div.price-and-size-wrapper > div.product-price > span.price-sales')
        if element:
            if element.text.strip() != '不适用':
                price_text = element.text.strip()[1:].replace(',', '')
                product['price'] = float(price_text)
        # images
        elements = utils.find_elements_by_css_selector(driver, 'ul.product-thumbnails-list > li > a')
        images = [element.get_attribute('href').strip() for element in elements]
        product['images'] = ';'.join(images)
        # detail
        details = []
        pattern = re.compile(r'<[^>]+>',re.S)
        elements = utils.find_elements_by_css_selector(driver, 'ul.details-col-1 > li')
        for element in elements:
            text = element.get_attribute('innerHTML').strip()
            text = pattern.sub('', text) # 去除HTML标签
            text = text.replace('\n\t\t', '')
            details.append(text)
        elements = utils.find_elements_by_css_selector(driver, 'ul.details-col-2 > li')
        for element in elements:
            text = element.get_attribute('innerHTML').strip()
            text = pattern.sub('', text)
            text = text.replace('\n\t\t', '')
            details.append(text)
        product['detail'] = '\n'.join(details)
        return product
