# 项目总览
该项目github url：https://github.com/KamisanaAtair/Emma-s-video-data-analyse.git
## 目标
- 阶段一：使用爬虫+bilibili公开api库爬取用户数据
- 阶段二：处理数据
- 阶段三：分析数据
	先使用所有视频数据横向对比出绘绘受众更偏爱的分区
	然后再每天更新一次数据记录数据变化
	尽可能将上述过程自动化
	然后试着引入数据库保存数据
## 技术栈
- 阶段一
	使用asyncio、bilibili_api、json
- 阶段二
	asyncio、bilibili_api、json
- 阶段三（未开发等待后续填写）
## 工作区文件结构
- ezuki emma `主目录`
	- 爬虫爬取绘绘数据并分析 `日志文件夹，将obsidian中日志更新到项目中`
	- main `主要代码放置区`
	- JSON_SAVE `放置爬取的json文件，确认可用后放置于此`
## 数据源
使用对bilibili绘魔emma进行爬取其视频数据，使用json结构储存
## 爬取字段
详见[[JSON_README]]

