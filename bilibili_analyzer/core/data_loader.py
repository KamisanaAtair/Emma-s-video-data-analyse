"""
数据加载器模块
负责从JSON文件加载视频数据，并进行基础的数据清洗和验证
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class DataLoader:
    """
    数据加载器类
    
    功能：
    1. 从JSON文件加载视频数据
    2. 数据验证和清洗
    3. 数据格式转换（JSON → DataFrame）
    """
    
    def __init__(self, data_file_path: str):
        """
        初始化数据加载器
        
        Args:
            data_file_path: 数据文件路径
        """
        self.data_file_path = Path(data_file_path)
        self.raw_data = None  # 原始数据
        self.df = None        # 处理后的DataFrame
        
    def load_json(self) -> Optional[List[Dict]]:
        """
        从JSON文件加载数据
        
        Returns:
            List[Dict]: 视频数据列表，如果加载失败返回None
        """
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ 成功加载 {len(data)} 条视频数据")
            self.raw_data = data
            return data
            
        except FileNotFoundError:
            print(f"✗ 错误：未找到数据文件 {self.data_file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"✗ 错误：JSON解析失败 - {e}")
            return None
        except Exception as e:
            print(f"✗ 错误：加载数据时出现未知错误 - {e}")
            return None
    
    def validate_data(self, data: List[Dict]) -> bool:
        """
        验证数据的完整性和有效性
        
        Args:
            data: 原始数据列表
            
        Returns:
            bool: 数据是否有效
        """
        if not data:
            print("✗ 数据验证失败：数据为空")
            return False
        
        # 必需字段（bv号、标题、播放、点赞、创建时间）
        required_fields = ['bvid', 'title', 'play', 'like', 'created']
        
        # 检查第一条数据是否包含必需字段
        first_item = data[0]
        missing_fields = [field for field in required_fields if field not in first_item]
        
        if missing_fields:
            print(f"✗ 数据验证失败：缺少必需字段 {missing_fields}")
            return False
        
        print("✓ 数据验证通过")
        return True
    
    def to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """
        将JSON数据转换为DataFrame，并进行基础处理
        
        Args:
            data: 原始数据列表
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 时间戳转换为日期时间
        df['created_date'] = pd.to_datetime(df['created'], unit='s')
        
        # 提取年月信息（用于时间序列分析）
        df['year'] = df['created_date'].dt.year
        df['month'] = df['created_date'].dt.month
        df['year_month'] = df['created_date'].dt.to_period('M')
        
        # 提取星期信息（用于发布时间分析）
        df['weekday'] = df['created_date'].dt.dayofweek  # 0=周一, 6=周日
        df['is_weekend'] = df['weekday'].isin([5, 6])
        
        # 视频时长转换（秒 → 分钟，保留小数）
        df['length_minutes'] = df['length'] / 60
        
        # 确保数值类型正确
        numeric_columns = ['play', 'like', 'coin', 'favorite', 'danmaku', 'share', 'comment', 'length']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 按发布时间排序
        df = df.sort_values('created_date').reset_index(drop=True)
        
        print(f"✓ 数据转换完成：{len(df)} 行 × {len(df.columns)} 列")
        print(f"  时间范围：{df['created_date'].min().strftime('%Y-%m-%d')} 至 {df['created_date'].max().strftime('%Y-%m-%d')}")
        
        self.df = df
        return df
    
    def get_basic_info(self) -> Dict:
        """
        获取数据基本信息
        
        Returns:
            Dict: 包含数据基本统计信息的字典
        """
        if self.df is None:
            print("Error：请先加载数据")
            return {}
        
        info = {
            'total_videos': len(self.df),
            'date_range': {
                'start': self.df['created_date'].min().strftime('%Y-%m-%d'),
                'end': self.df['created_date'].max().strftime('%Y-%m-%d'),
                'days': (self.df['created_date'].max() - self.df['created_date'].min()).days
            },
            'total_plays': self.df['play'].sum(),
            'total_likes': self.df['like'].sum(),
            'total_coins': self.df['coin'].sum(),
            'total_favorites': self.df['favorite'].sum(),
            'total_comments': self.df['comment'].sum(),
            'avg_play': self.df['play'].mean(),
            'median_play': self.df['play'].median(),
            'categories': self.df['typeid'].value_counts().to_dict()
        }
        
        return info
    
    def print_summary(self):
        """
        打印数据摘要信息（美化输出）
        """
        if self.df is None:
            print("Error：请先加载数据")
            return
        
        info = self.get_basic_info()
        
        print("\n" + "="*60)
        print("📊 数据摘要信息")
        print("="*60)
        print(f"视频总数：{info['total_videos']} 个")
        print(f"时间跨度：{info['date_range']['start']} 至 {info['date_range']['end']} ({info['date_range']['days']} 天)")
        print(f"\n播放数据：")
        print(f"  - 总播放量：{info['total_plays']:,}")
        print(f"  - 平均播放：{info['avg_play']:.0f}")
        print(f"  - 中位播放：{info['median_play']:.0f}")
        print(f"\n互动数据：")
        print(f"  - 总点赞数：{info['total_likes']:,}")
        print(f"  - 总投币数：{info['total_coins']:,}")
        print(f"  - 总收藏数：{info['total_favorites']:,}")
        print(f"  - 总评论数：{info['total_comments']:,}")
        print("="*60 + "\n")
    
    def load_and_process(self) -> Optional[pd.DataFrame]:
        """
        一键完成：加载 → 验证 → 转换
        
        Returns:
            pd.DataFrame: 处理后的数据，失败返回None
        """
        # 加载数据
        data = self.load_json()
        if data is None:
            return None
        
        # 验证数据
        if not self.validate_data(data):
            return None
        
        # 转换为DataFrame
        df = self.to_dataframe(data)
        
        # 打印摘要
        self.print_summary()
        
        return df


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 示例：如何使用DataLoader
    
    from pathlib import Path
    
    # 数据文件路径
    data_file = Path(__file__).parent.parent.parent / "JSON_SAVE" / "analytics_SAVE.json"
    
    # 创建加载器实例
    loader = DataLoader(data_file)
    
    # 方法1：一键加载和处理
    df = loader.load_and_process()
    
    if df is not None:
        print("数据加载成功！")
        print(f"数据形状：{df.shape}")
        print(f"\n前3条数据：")
        print(df[['title', 'play', 'like', 'created_date']].head(3))
