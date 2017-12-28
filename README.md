# sc_fashion
基于scrapy的时尚网站商品数据抓取

1. 解决了selenium与scrapy合作的效率问题。调用scrapy.Request(...)先访问localhost, url通过meta传递。
2. 使用mysql与redis进行任务与工作管理，断点继续轻松搞定。
