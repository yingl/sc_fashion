# -*- coding: utf-8 -*-
import scrapy
import traceback
from sc_fashion.extras import product_config as config
from sc_fashion.extras import scf_database as database
from sc_fashion.extras import scf_queue as queue
from sc_fashion.extras import utils


class ProductDgSpider(scrapy.Spider):
    name = 'product_dg'
    brand = 'dolce&gabbana'
    allowed_domains = ['www.dolcegabbana.com.cn']

    def start_requests(self):
        database.init_database(config.db)
        for job in utils.fetch_jobs(database, queue, config):
            url = job['url']
            meta = job
            meta['config'] = config
            meta['database'] = database
            meta['parse'] = self.parse_page
            if utils.check_domain(url, ProductDgSpider.allowed_domains):
                yield scrapy.Request(url, callback=utils.parse, dont_filter=True, meta=meta)

    def parse_page(self, driver, url):
        product = {'url': url,
                   'brand': ProductDgSpider.brand,
                   'code': '',
                   'price': 0,
                   'images': '',
                   'detail': ''}
        # check 404
        element = utils.find_element_by_css_selector(driver, 'div.b-error_page-wrapper')
        if element:
            raise Exception('404 page not found')
        # Switch to CHN
        element = utils.find_elements_by_css_selector(driver, 'ul.l-header_service_menu > li > span')[0]
        driver.execute_script('arguments[0].click();', element)
        utils.sleep(1)
        element = utils.find_elements_by_css_selector(driver, 'ul.b-language_selector-language_list > li > a')[-1]
        driver.execute_script('arguments[0].click();', element)
        utils.sleep(1)
        # title
        element = utils.find_element_by_css_selector(driver, 'span.b-product_name')
        if element:
            product['title'] = element.text.strip()
        else:
            raise Exception('Title not found for %s' % driver.current_url)
        # code
        element = utils.find_element_by_css_selector(driver, 'div.b-product_master_id')
        product['code'] = element.get_attribute('innerHTML').split('：')[1].strip()
        # unit
        product['unit'] = config.rmb
        # price
        element = utils.find_element_by_css_selector(driver, 'h4.b-product_price-standard')
        if element:
            price_text = element.text.strip()[1:].replace(',', '')
            try:
                product['price'] = float(price_text)
            except:
                pass # 有那么几件商品没价格
        # images
        images = []
        elements = utils.find_elements_by_css_selector(driver, 'div.js-thumbnails_slider > ul.js-thumbnails > li > img')
        for element in elements:
            text = element.get_attribute('src').strip()
            images.append(text.split('?')[0])
        product['images'] = ';'.join(images)
        # detail
        element = utils.find_element_by_css_selector(driver, 'div.b-product_long_description')
        text = element.get_attribute('innerHTML')
        text = text[1:] # Remove the first '\n'
        text = text.replace('amp;', '')
        text = text.replace('。', '。\n')
        text = text.replace('<i>', '')
        text = text.replace('</i>', '')
        text = text.replace('<br>', '')
        text = text.replace('• ', '\n• ')
        product['detail'] = text[:-2] # Remove the tailing '\n'
        return product