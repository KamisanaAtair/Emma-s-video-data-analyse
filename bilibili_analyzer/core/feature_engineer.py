"""
特征工程模块
负责从原始数据中提取和构造新的特征，用于后续分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config


class FeatureEngineer:
    """
    特征工程类
    
    功能：
    1. 计算各类互动率指标
    2. 视频分类和标注
    3. 构造衍生特征
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化特征工程器
        
        Args:
            df: 原始数据DataFrame
        """
        self.df = df.copy()  # 复制数据，避免修改原始数据
        
    def calculate_engagement_rates(self) -> pd.DataFrame:
        """
        计算各类互动率
        
        互动率 = 互动数 / 播放量 × 100%
        包括：点赞率、投币率、收藏率、分享率、评论率、弹幕率
        
        Returns:
            pd.DataFrame: 添加了互动率列的数据
        """
        # 避免除以0，将播放量为0的替换为1
        safe_play = self.df['play'].replace(0, 1)
        
        # 计算各类互动率（百分比）
        self.df['like_rate'] = (self.df['like'] / safe_play * 100).round(2)
        self.df['coin_rate'] = (self.df['coin'] / safe_play * 100).round(2)
        self.df['favorite_rate'] = (self.df['favorite'] / safe_play * 100).round(2)
        self.df['share_rate'] = (self.df['share'] / safe_play * 100).round(2)
        self.df['comment_rate'] = (self.df['comment'] / safe_play * 100).round(2)
        self.df['danmaku_rate'] = (self.df['danmaku'] / safe_play * 100).round(2)
        
        # 计算综合互动率（加权平均）
        weights = config.ENGAGEMENT_WEIGHTS
        self.df['engagement_rate'] = (
            self.df['like_rate'] * weights['like_rate'] +
            self.df['coin_rate'] * weights['coin_rate'] +
            self.df['favorite_rate'] * weights['favorite_rate'] +
            self.df['comment_rate'] * weights['comment_rate']
        ).round(2)
        
        print("✓ 互动率计算完成")
        return self.df
    
    def categorize_video_length(self) -> pd.DataFrame:
        """
        视频时长分类
        
        将视频按时长分为不同类别：<30秒、30秒-1分钟、1-3分钟等
        
        Returns:
            pd.DataFrame: 添加了时长分类列的数据
        """
        self.df['length_category'] = pd.cut(
            self.df['length'],
            bins=config.LENGTH_BINS,
            labels=config.LENGTH_LABELS,
            right=False
        )
        
        print("✓ 视频时长分类完成")
        return self.df
    
    def categorize_play_count(self) -> pd.DataFrame:
        """
        播放量分类
        
        将视频按播放量分为不同档次
        
        Returns:
            pd.DataFrame: 添加了播放量分类列的数据
        """
        self.df['play_category'] = pd.cut(
            self.df['play'],
            bins=config.PLAY_BINS,
            labels=config.PLAY_LABELS,
            right=False
        )
        
        print("✓ 播放量分类完成")
        return self.df
    
    def classify_content_type(self) -> pd.DataFrame:
        """
        内容类型分类
        
        根据标题关键词自动分类视频类型
        例如：游戏切片、唱歌、模型展示等
        
        Returns:
            pd.DataFrame: 添加了内容类型列的数据
        """
        def get_content_type(title: str) -> str:
            """根据标题判断内容类型"""
            title = str(title).lower()
            
            for content_type, keywords in config.CONTENT_TYPE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword.lower() in title:
                        return content_type
            
            # 默认类型：根据分区判断
            return "其他"
        
        self.df['content_type'] = self.df['title'].apply(get_content_type)
        
        print("✓ 内容类型分类完成")
        print(f"  类型分布：{self.df['content_type'].value_counts().to_dict()}")
        return self.df
    
    def identify_viral_videos(self) -> pd.DataFrame:
        """
        识别爆款视频
        
        根据配置的阈值标记爆款视频
        标准：
        1. 播放量 > 平均值的N倍
        2. 或播放量 > 某个绝对值
        3. 且互动率较高
        
        Returns:
            pd.DataFrame: 添加了爆款标记列的数据
        """
        threshold = config.VIRAL_VIDEO_THRESHOLD
        
        # 计算播放量阈值
        avg_play = self.df['play'].mean()
        threshold_1 = avg_play * threshold['play_multiplier']
        threshold_2 = threshold['min_play_count']
        
        # 标记爆款视频
        self.df['is_viral'] = (
            ((self.df['play'] > threshold_1) | (self.df['play'] > threshold_2)) &
            (self.df['engagement_rate'] > threshold['min_engagement_rate'])
        )
        
        viral_count = self.df['is_viral'].sum()
        print(f"✓ 爆款视频识别完成：共 {viral_count} 个爆款")
        
        return self.df
    
    def calculate_performance_index(self) -> pd.DataFrame:
        """
        计算综合表现指数
        
        一个0-100的分数，综合考虑播放量、互动率等因素
        用于快速评估视频表现
        
        Returns:
            pd.DataFrame: 添加了表现指数列的数据
        """
        # 播放量归一化（0-100）
        play_max = self.df['play'].max()
        play_normalized = (self.df['play'] / play_max * 100) if play_max > 0 else 0
        
        # 互动率已经是百分比，直接使用
        engagement_normalized = self.df['engagement_rate']
        
        # 综合指数（50%播放量 + 50%互动率）
        self.df['performance_index'] = (
            play_normalized * 0.5 + engagement_normalized * 0.5
        ).round(1)
        
        print("✓ 综合表现指数计算完成")
        return self.df
    
    def add_title_features(self) -> pd.DataFrame:
        """
        提取标题特征
        
        包括：标题长度、是否包含表情、是否使用标签等
        
        Returns:
            pd.DataFrame: 添加了标题特征列的数据
        """
        # 标题长度
        self.df['title_length'] = self.df['title'].str.len()
        
        # 是否使用【】标签
        self.df['has_bracket_tag'] = self.df['title'].str.contains('【|】', regex=True)
        
        # 是否包含表情符号（简单判断）
        self.df['has_emoji'] = self.df['title'].str.contains('❤|💜|✨|🎮|🎵', regex=True)
        
        print("✓ 标题特征提取完成")
        return self.df
    
    def calculate_roi(self) -> pd.DataFrame:
        """
        计算ROI（投资回报率）
        
        这里用"播放量/视频时长"作为简单的ROI指标
        表示每秒视频时长带来的播放量
        
        Returns:
            pd.DataFrame: 添加了ROI列的数据
        """
        # 避免除以0
        safe_length = self.df['length'].replace(0, 1)
        
        self.df['roi'] = (self.df['play'] / safe_length).round(2)
        
        print("✓ ROI计算完成")
        return self.df
    
    def engineer_all_features(self) -> pd.DataFrame:
        """
        一键执行所有特征工程
        
        按顺序执行所有特征构造方法
        
        Returns:
            pd.DataFrame: 包含所有新特征的数据
        """
        print("\n" + "="*60)
        print("🔧 开始特征工程...")
        print("="*60)
        
        # 执行所有特征工程
        self.calculate_engagement_rates()
        self.categorize_video_length()
        self.categorize_play_count()
        self.classify_content_type()
        self.identify_viral_videos()
        self.calculate_performance_index()
        self.add_title_features()
        self.calculate_roi()
        
        print("="*60)
        print(f"✓ 特征工程完成！新增 {len(self.df.columns) - len(self.df.columns)} 个特征")
        print("="*60 + "\n")
        
        return self.df
    
    def get_feature_summary(self) -> Dict:
        """
        获取特征统计摘要
        
        Returns:
            Dict: 特征统计信息
        """
        summary = {
            'engagement': {
                'avg_like_rate': self.df['like_rate'].mean(),
                'avg_coin_rate': self.df['coin_rate'].mean(),
                'avg_favorite_rate': self.df['favorite_rate'].mean(),
                'avg_comment_rate': self.df['comment_rate'].mean(),
                'avg_engagement_rate': self.df['engagement_rate'].mean()
            },
            'length_distribution': self.df['length_category'].value_counts().to_dict(),
            'content_type_distribution': self.df['content_type'].value_counts().to_dict(),
            'viral_videos': {
                'count': self.df['is_viral'].sum(),
                'percentage': (self.df['is_viral'].sum() / len(self.df) * 100)
            },
            'performance': {
                'avg_performance_index': self.df['performance_index'].mean(),
                'max_performance_index': self.df['performance_index'].max()
            }
        }
        
        return summary


# ==================== 使用示例 ====================
if __name__ == "__main__":
    from data_loader import DataLoader
    
    # 加载数据
    data_file = Path(__file__).parent.parent.parent / "JSON_SAVE" / "analytics_SAVE.json"
    loader = DataLoader(data_file)
    df = loader.load_and_process()
    
    if df is not None:
        # 特征工程
        engineer = FeatureEngineer(df)
        df_engineered = engineer.engineer_all_features()
        
        print("\n特征工程后的数据示例：")
        print(df_engineered[['title', 'play', 'engagement_rate', 'content_type', 'is_viral']].head())
        
        # 打印特征摘要
        summary = engineer.get_feature_summary()
        print("\n特征摘要：")
        print(f"平均互动率：{summary['engagement']['avg_engagement_rate']:.2f}%")
        print(f"爆款视频数：{summary['viral_videos']['count']} ({summary['viral_videos']['percentage']:.1f}%)")
