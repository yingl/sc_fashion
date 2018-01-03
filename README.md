# sc_fashion
基于scrapy的时尚网站商品数据抓取

主要工作
1. 解决了selenium与scrapy合作的效率问题。调用scrapy.Request(...)先访问localhost, url通过meta传递。
2. 使用mysql与redis进行任务（task）与工作（job）管理，断点继续轻松搞定。
3. 使用了redis进行工作分发之后，如果不够快就多台机器一起上。
4. 数据整理去重脚本也完善了。

关于entry和product的解释
- entry是入口页面，先通过entry页面抓取商品链接。
- product是具体商品，抓取商品详情。
- extra/scripts是相关辅助脚本，用于数据导入导出和任务调度等工作。

任务调度
- scheduler.py，参数解释如下：
  - -c/--config: 配置文件，entry使用entry_config，product使用product_config。
  - -a/--action：操作类型，create创建新task，view查看task状态，
  - -r/--retry：重试某个task失败或未完成的job
  - -tid/--task_id：指定task的id，用于view或retry操作。
  - -d/--domain：处理链接的域名，比如www.ferragamo.cn。

入口页面相关操作：
- 原始数据导入：write_entries.py -f entries/xxx.txt -c entry_config（-c参数可使用默认）
- 商品列表导出：output_products.py -f products/xxx.txt（输出路径） -t 5（指定task的id，输出结果） -c entry_config（-c参数可使用默认）

商品页相关操作
- 原始数据导入：write_products.py -f products/xxx.txt -c product_config（-c参数可使用默认）
- 商品详情导出：output_details.py -f details/xxx.txt -t 5（指定task的id，输出结果） -c entry_config（-c参数可使用默认）
