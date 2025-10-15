import asyncio
from bilibili_api import video, sync
import json

def load_basic_data():
    """加载已有的基本数据"""
    try:
        with open("user_videos_data.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("未找到 user_videos_data.json 文件，请先运行主爬虫脚本")
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
            'view': stat.get('view', 0),      # 播放量
            'like': stat.get('like', 0),      # 点赞数
            'coin': stat.get('coin', 0),      # 投币数
            'favorite': stat.get('favorite', 0),  # 收藏数
            'danmaku': stat.get('danmaku', 0),   # 弹幕数
            'share': stat.get('share', 0),    # 分享数
            'reply': stat.get('reply', 0),    # 评论数
        }
        
        return detail_data
    except Exception as e:
        print(f"获取视频 {bvid} 详细信息时出错: {e}")
        return None

def update_analytics_data(basic_data, detailed_stats):
    """
    更新分析数据，添加详细的互动统计数据
    
    Args:
        basic_data (list): 基本分析数据
        detailed_stats (list): 详细统计数据
        
    Returns:
        list: 更新后的分析数据
    """
    # 创建BV号到详细数据的映射
    stats_map = {stat['bvid']: stat for stat in detailed_stats if stat}
    
    # 更新每条数据
    updated_data = []
    for data in basic_data:
        bvid = data['bvid']
        updated_item = data.copy()
        
        # 如果有详细数据，则更新互动统计数据
        if bvid in stats_map:
            stat = stats_map[bvid]
            updated_item['like'] = stat['like']
            updated_item['coin'] = stat['coin']
            updated_item['favorite'] = stat['favorite']
            updated_item['danmaku'] = stat['danmaku']
            updated_item['share'] = stat['share']
            # 注意：播放量和评论数可能与原数据不同，这里保持原数据
        
        updated_data.append(updated_item)
    
    return updated_data

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
    videos_data = load_basic_data()
    if not videos_data:
        return
    
    # 获取视频列表
    video_list = videos_data.get('list', {}).get('vlist', [])
    
    # 获取所有视频的详细统计数据
    print("正在获取视频详细统计数据...")
    detailed_stats = []
    
    for i, video_item in enumerate(video_list):
        bvid = video_item.get('bvid')
        title = video_item.get('title', '')[:30] + '...' if len(video_item.get('title', '')) > 30 else video_item.get('title', '')
        
        print(f"({i+1}/{len(video_list)}) 正在获取视频 '{title}' 的详细信息...")
        stat = await get_video_detail(bvid)
        detailed_stats.append(stat)
        
        # 添加延迟以避免请求过于频繁
        await asyncio.sleep(0.5)
    
    # 加载现有的分析数据
    try:
        with open("analytics_data.json", 'r', encoding='utf-8') as f:
            basic_analytics_data = json.load(f)
    except FileNotFoundError:
        print("未找到 analytics_data.json 文件")
        return
    
    # 更新分析数据
    updated_analytics_data = update_analytics_data(basic_analytics_data, detailed_stats)
    
    # 保存更新后的数据
    save_to_json(updated_analytics_data, "analytics_data_detailed.json")
    
    # 显示结果
    print("\n详细统计数据获取完成！")
    print(f"共处理 {len(updated_analytics_data)} 个视频")
    
    # 显示前几个视频的详细数据
    print("\n前5个视频的详细统计数据:")
    for i, data in enumerate(updated_analytics_data[:5]):
        print(f"{i+1}. {data['title']}")
        print(f"   BV号: {data['bvid']}")
        print(f"   播放量: {data['play']}")
        print(f"   点赞数: {data['like']}")
        print(f"   投币数: {data['coin']}")
        print(f"   收藏数: {data['favorite']}")
        print(f"   弹幕数: {data['danmaku']}")
        print(f"   分享数: {data['share']}")
        print(f"   评论数: {data['comment']}")
        print("-" * 40)

if __name__ == "__main__":
    sync(main())