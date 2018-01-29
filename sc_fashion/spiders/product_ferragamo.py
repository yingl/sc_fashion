# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import product_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class ProductFerragamoSpider(scrapy.Spider):
    name = 'product_ferragamo'
    brand = 'ferragamo'
    allowed_domains = ['www.ferragamo.cn']

    def start_requests(self):
        database.init_database(config.db)
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            meta = job
            meta['config'] = config
            meta['database'] = database
            meta['parse'] = self.parse_page
            if utils.check_domain(url, ProductFerragamoSpider.allowed_domains):
                yield scrapy.Request(url, callback=utils.parse, dont_filter=True, meta=meta)

    def parse_page(self, driver, url):
        products = []
        product = {'url': url,
                   'brand': ProductFerragamoSpider.brand,
                   'code': '',
                   'price': 0,
                   'images': '',
                   'detail': ''}
        # check 404
        element = utils.find_element_by_css_selector(driver, 'div.nofound')
        if element:
            raise Exception('404 page not found')
        # title
        element = utils.find_element_by_css_selector(driver, 'div.dpd-main__details__head > div > h1.dpd-main__name')
        if element:
            product['title'] = element.text.strip()
        else:
            raise Exception('Title not found for %s' % driver.current_url)
        # code
        element = utils.find_element_by_css_selector(driver, 'div.dpd-main__details__head > div > div.dpd-main__sku')
        if element:
            product['code'] = ' '.join(element.text.strip().split(' ')[1:])
        # unit
        product['unit'] = config.rmb
        # price
        element = utils.find_element_by_css_selector(driver, 'div.dpd-main__details__head > div > div.dpd-main__price')
        if element:
            product['price'] = float(element.text.strip().split(' ')[1])
        # images
        elements = utils.find_elements_by_css_selector(driver, 'div.dpd-visuals > div > a > img')
        images = [element.get_attribute('src').strip() for element in elements]
        product['images'] = ';'.join(images)
        # detail
        element = utils.find_element_by_css_selector(driver, 'div.dpd-info__body')
        if element:
            product['detail'] = element.get_attribute('innerHTML').strip()
        return product
