'''
我创建了一个新的脚本 detailed_video_stats.py，该脚本可以：

加载已有的基本数据
通过视频BV号逐个获取每个视频的详细统计数据
生成包含完整互动数据的 analytics_data.json 文件
'''
import asyncio
from bilibili_api import video, sync
import json

def load_basic_data():
    """加载已有的基本数据"""
    try:
        with open("basic_data.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("未找到 basic_data.json 文件，请先运行主爬虫脚本")
        return None

async def get_video_detail(bvid):
    """
    获取单个视频的详细信息
    
    Args:
        bvid (str): 视频的BV号
        
    Returns:
        dict: 视频详细信息
    """
    try:
        # 创建视频对象
        v = video.Video(bvid=bvid)
        
        # 获取视频信息
        info = await v.get_info()
        
        # 提取需要的统计数据
        stat = info.get('stat', {})
        detail_data = {
            'bvid': bvid,
            'title': info.get('title', ''),
            'typeid': info.get('tid', 0),
            'created': info.get('pubdate', 0),
            'length': info.get('duration', 0),  # 以秒为单位
            'play': stat.get('view', 0),      # 播放量
            'like': stat.get('like', 0),      # 点赞数
            'coin': stat.get('coin', 0),      # 投币数
            'favorite': stat.get('favorite', 0),  # 收藏数
            'danmaku': stat.get('danmaku', 0),   # 弹幕数
            'share': stat.get('share', 0),    # 分享数
            'comment': stat.get('reply', 0),    # 评论数
        }
        
        return detail_data
    except Exception as e:
        print(f"获取视频 {bvid} 详细信息时出错: {e}")
        return None

def save_to_json(data, filename):
    """
    保存数据到JSON文件
    
    Args:
        data (dict/list): 要保存的数据
        filename (str): 文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存至 {filename}")

async def main():
    """主函数"""
    # 加载基本数据
    basic_data = load_basic_data()
    if not basic_data:
        return
    
    # 获取所有视频的详细统计数据
    print("正在获取视频详细统计数据...")
    detailed_stats = []
    
    for i, video_item in enumerate(basic_data):
        bvid = video_item.get('bvid')
        title = video_item.get('title', '')[:30] + '...' if len(video_item.get('title', '')) > 30 else video_item.get('title', '')
        
        print(f"({i+1}/{len(basic_data)}) 正在获取视频 '{title}' 的详细信息...")
        stat = await get_video_detail(bvid)
        detailed_stats.append(stat)
        
        # 添加延迟以避免请求过于频繁
        await asyncio.sleep(0.5)
    
    # 保存详细统计数据
    save_to_json(detailed_stats, "analytics_data.json")
    
    # 显示结果
    print("\n详细统计数据获取完成！")
    print(f"共处理 {len(detailed_stats)} 个视频")
    print("OK!go to the next step!")

if __name__ == "__main__":
    sync(main())