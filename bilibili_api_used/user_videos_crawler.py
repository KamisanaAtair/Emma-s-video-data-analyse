import asyncio
from bilibili_api import user, sync
import json

# 目标用户UID
TARGET_UID = 3493123242068319

async def get_user_videos(uid):
    """
    获取用户的投稿视频数据
    
    Args:
        uid (int): 用户的UID
        
    Returns:
        dict: 包含用户视频数据的字典
    """
    # 创建用户对象
    u = user.User(uid=uid)
    
    # 获取用户投稿视频列表
    # 默认获取第一页，每页30条数据
    videos_data = await u.get_videos()
    
    return videos_data

def extract_analytics_data(videos_data):
    """
    从视频数据中提取用于分析的关键维度数据
    
    Args:
        videos_data (dict): 包含用户视频数据的字典
        
    Returns:
        list: 包含用于分析的数据列表
    """
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
            'play': video.get('play', 0),      # 播放量
            'comment': video.get('comment', 0)  # 评论数
        }
        
        # 处理互动数据 - 检查是否有meta数据（系列视频）
        meta = video.get('meta')
        if meta and 'stat' in meta:
            # 系列视频从meta.stat提取数据
            stat = meta['stat']
            data_point['like'] = stat.get('like', 0)      # 点赞数
            data_point['coin'] = stat.get('coin', 0)      # 投币数
            data_point['favorite'] = stat.get('favorite', 0)  # 收藏数
            data_point['danmaku'] = stat.get('danmaku', 0)   # 弹幕数
            data_point['share'] = stat.get('share', 0)    # 分享数
        else:
            # 普通视频暂时将互动数据设为0，需要通过其他API获取完整数据
            data_point['like'] = 0
            data_point['coin'] = 0
            data_point['favorite'] = 0
            data_point['danmaku'] = 0
            data_point['share'] = 0
            
        analytics_data.append(data_point)
        
    return analytics_data

def save_to_json(data, filename="user_videos_data.json"):
    """
    将数据保存为JSON文件
    
    Args:
        data (dict): 要保存的数据
        filename (str): 保存的文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存至 {filename}")

def main():
    """
    主函数
    """
    try:
        # 获取用户视频数据
        videos_data = sync(get_user_videos(TARGET_UID))
        
        # 提取用于分析的数据
        analytics_data = extract_analytics_data(videos_data)
        
        # 保存完整数据到文件
        save_to_json(videos_data, "user_videos_data.json")
        
        # 保存分析用数据到单独文件
        save_to_json(analytics_data, "analytics_data.json")
        
        # 输出基本信息
        print(f"成功获取用户 {TARGET_UID} 的视频数据")
        print(f"视频总数: {videos_data.get('page', {}).get('count', 0)}")
        print(f"当前页视频数: {len(videos_data.get('list', {}).get('vlist', []))}")
        
        # 显示前几个视频的基本信息
        video_list = videos_data.get('list', {}).get('vlist', [])
        print("\n最新视频信息:")
        for i, video in enumerate(video_list[:5]):  # 显示前5个视频
            print(f"{i+1}. 标题: {video.get('title', 'N/A')}")
            print(f"   BV号: {video.get('bvid', 'N/A')}")
            print(f"   播放量: {video.get('play', 'N/A')}")
            print(f"   创建时间: {video.get('created', 'N/A')}")
            print(f"   时长: {video.get('length', 'N/A')}")
            
            # 如果有meta数据，显示更多互动数据
            meta = video.get('meta')
            if meta and 'stat' in meta:
                stat = meta['stat']
                print(f"   点赞数: {stat.get('like', 'N/A')}")
                print(f"   投币数: {stat.get('coin', 'N/A')}")
                print(f"   收藏数: {stat.get('favorite', 'N/A')}")
            print("-" * 40)
            
        # 显示分区信息
        tlist = videos_data.get('list', {}).get('tlist', {})
        print("\n分区分布:")
        for typeid, info in tlist.items():
            print(f"  {info.get('name', 'N/A')} (ID: {typeid}): {info.get('count', 0)} 个视频")
            
    except Exception as e:
        print(f"获取数据时出错: {e}")

if __name__ == "__main__":
    main()