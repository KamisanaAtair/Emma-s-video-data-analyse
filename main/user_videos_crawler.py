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
    
    # 获取用户投稿视频列表的第一页，以获取视频总数和其他分页信息
    first_page_data = await u.get_videos(pn=1, ps=30)
    
    # 获取视频总数
    total_count = first_page_data.get('page', {}).get('count', 0)
    print(f"UP主共有 {total_count} 个视频")
    
    # 计算总页数（每页30条数据）
    pages = (total_count + 29) // 30  # 向上取整
    print(f"需要获取 {pages} 页数据")
    
    # 如果只有一页，直接返回第一页数据
    if pages <= 1:
        return first_page_data
    
    # 合并所有页面的数据
    all_videos = first_page_data.get('list', {}).get('vlist', []).copy()
    
    # 获取剩余页面的数据
    for page in range(2, pages + 1):
        print(f"正在获取第 {page}/{pages} 页数据...")
        page_data = await u.get_videos(pn=page, ps=30)
        page_videos = page_data.get('list', {}).get('vlist', [])
        all_videos.extend(page_videos)
        # 添加延迟以避免请求过于频繁
        await asyncio.sleep(0.5)
    
    # 构造完整的数据结构
    result = first_page_data.copy()
    result['list'] = result.get('list', {}).copy()
    result['list']['vlist'] = all_videos
    result['page'] = result.get('page', {}).copy()
    result['page']['count'] = len(all_videos)
    
    return result

def extract_basic_data(videos_data):
    """
    从视频数据中提取基本数据（仅BV号用于后续详细数据获取）

    Args:
        videos_data (dict): 包含用户视频数据的字典
        
    Returns:
        list: 包含基本数据的列表
    """
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
        videos_data = sync(get_user_videos(TARGET_UID))# sync函数属于bilibili_api库
        
        # 提取基本数据
        basic_data = extract_basic_data(videos_data)
        
        # 保存完整数据到文件
        save_to_json(videos_data, "user_videos_data.json")
        
        # 保存基本数据到单独文件
        save_to_json(basic_data, "basic_data.json")
        
        # 输出基本信息
        print(f"成功获取用户 {TARGET_UID} 的视频数据")
        print(f"视频总数: {videos_data.get('page', {}).get('count', 0)}")
        print(f"当前页视频数: {len(videos_data.get('list', {}).get('vlist', []))}")
        print("Bro,everything is OK!")        
          
    except Exception as e:
        print(f"获取数据时出错: {e}")

if __name__ == "__main__":
    main()