# 调试selenium爬虫实现
import sys
sys.path.append('../')
import product_config as config
import utils

if __name__ == '__main__':
    url = 'https://www.ferragamo.cn/item-8058571809128.html'
    driver = utils.create_chrome_driver()
    driver.get(url)
    print(dir(driver))
    '''
    product = {'brand': 'brand',
               'code': '',
               'price': 0,
               'images': '',
               'detail': ''}
    # title
    element = utils.find_element_by_css_selector(driver, 'div.dpd-main__details__head > div > h1.dpd-main__name')
    if element:
        product['title'] = element.text.strip()
    else:
        raise Exception('Title not found for %s' % driver.current_url)
    # code
    element = utils.find_element_by_css_selector(driver, 'div.dpd-main__details__head > div > div.dpd-main__sku')
    if element:
        product['code'] = element.text.strip()
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
    print(element)
    if element:
        product['detail'] = element.get_attribute('innerHTML').strip()
    print(product)
    '''
    driver.quit()
