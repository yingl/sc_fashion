# sc_fashion
基于scrapy的时尚网站商品数据抓取

1. 解决了selenium与scrapy合作的效率问题。调用scrapy.Request(...)先访问localhost, url通过meta传递。
2. 使用mysql与redis进行任务（task）与工作（job）管理，断点继续轻松搞定。
3. 使用了redis进行工作分发之后，如果不够快就多台机器一起上。
4. 数据整理去重脚本也完善了。
