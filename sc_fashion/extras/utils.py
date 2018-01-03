import time
import traceback
from selenium import webdriver

def sleep(seconds):
    time.sleep(seconds)

def create_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    return driver

def find_element_by_css_selector(element, selector):
    try:
        return element.find_element_by_css_selector(selector)
    except:
        return None

def find_elements_by_css_selector(element, selector):
    try:
        return element.find_elements_by_css_selector(selector)
    except:
        return []

def check_domain(url, domains):
    for domain in domains:
        if domain in url:
            print('%s, %s is True' % (domain, url))
            return True
    return False

def fetch_jobs(database, queue, config):
    # 从redis队列获取工作任务
    # 这里用无限循环会卡死的，如果真要用可以考虑异步sleep。
    try:
        tasks = database.Task
        for task in tasks.select().where(tasks.status == config.ts_inprogress):
            queue_ = queue.Queue(task.id, config.queue)
            while not queue_.empty():
                job = queue_.get(False)
                if job:
                    yield eval(job)
    except Exception as e:
        print('%s\n%s' % (e, traceback.format_exc()))
    return 'Done'    

def build_result(meta):
    result = {}
    result['job_id'] = meta['id']
    result['source_id'] = meta['source_id']
    result['content'] = ''
    result['message'] = '' # 失败原因
    return result

def parse(parse_page, meta, config):
    driver = None
    url = meta['url']
    result = build_result(meta)
    try:
        driver = create_chrome_driver()
        result['content'] = parse_page(driver, url)
        result['status'] = config.js_finished
    except Exception as e:
        result['message'] = '%s\n%s' % (e, traceback.format_exc())
        result['status'] = config.js_failed
    finally:
        if driver:
            driver.quit()
    return result