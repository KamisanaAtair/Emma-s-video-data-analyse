```python
def extract_analytics_data(videos_data):
    analytics_data = []

    # 遍历视频列表
    video_list = videos_data.get('list', {}).get('vlist', [])
    for video in video_list:

        # 提取基本数据维度
        data_point = {

            # 基本信息
            'title': video.get('title', ''),
            'bvid': video.get('bvid', ''),
            'typeid': video.get('typeid', 0),
            'created': video.get('created', 0),
            'length': video.get('length', ''),
            # 互动数据 - 从视频对象本身提取
            'play': video.get('play', 0),      # 播放量
            'comment': video.get('comment', 0)  # 评论数
        }

        # 处理互动数据 - 检查是否有meta数据（系列视频）
        meta = video.get('meta')
        if meta and 'stat' in meta:

            # 系列视频从meta.stat提取数据
            stat = meta['stat']
            data_point['like'] = stat.get('like', 0)      # 点赞数
            data_point['coin'] = stat.get('coin', 0)      # 投币数
            data_point['favorite'] = stat.get('favorite', 0)  # 收藏数
            data_point['danmaku'] = stat.get('danmaku', 0)   # 弹幕数
            data_point['share'] = stat.get('share', 0)    # 分享数
        else:

            # 普通视频暂时将互动数据设为0，需要通过其他API获取完整数据
            data_point['like'] = 0
            data_point['coin'] = 0
            data_point['favorite'] = 0
            data_point['danmaku'] = 0
            data_point['share'] = 0
        analytics_data.append(data_point)
    return analytics_data
```
# error
该文件中使用get_videos函数获取的信息有限，无法获取精确信息
存在detailed_video_stats文件通过bv号逐一获取全部精确信息，意味着该函数中除了bv号全是冗余数据而且数据量不够，让detailed_video_stats的作用性更强、主爬虫中该函数更简洁目的性更强
# 更正思路
让该函数仅负责获取bv号，交给脚本完全处理所有信息获取
# 更正代码
```python
def extract_basic_data(videos_data):
    basic_data = []

    # 遍历视频列表
    video_list = videos_data.get('list', {}).get('vlist', [])
    for video in video_list:

        # 只提取BV号，用于后续详细数据获取
        data_point = {
            'title': video.get('title', ''),
            'bvid': video.get('bvid', ''),
            'typeid': video.get('typeid', 0),
            'created': video.get('created', 0),
            'length': video.get('length', ''),
            'play': video.get('play', 0),
            'comment': video.get('comment', 0)
        }

        basic_data.append(data_point)
    return basic_data
```
- 我确实只需要bv号，但是仍然需要保留一些字段来保证数据结构不会被改变，来最小限度更改其他部分代码