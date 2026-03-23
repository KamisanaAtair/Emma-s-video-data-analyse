"""
指标计算模块
负责计算各类高级分析指标和统计数据
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config


class MetricsCalculator:
    """
    指标计算器类
    
    功能：
    1. 计算视频质量评分
    2. 计算各类统计指标
    3. 进行对比分析
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化指标计算器
        
        Args:
            df: 已经过特征工程的DataFrame
        """
        self.df = df
        
    def calculate_quality_score(self) -> pd.DataFrame:
        """
        计算视频质量评分（0-100分）
        
        质量分组成：
        1. 播放吸引力分 (30%)：基于播放量的相对表现
        2. 内容质量分 (40%)：基于互动率
        3. 传播力分 (20%)：基于分享率和评论数
        4. 持久性分 (10%)：基于视频长尾效应（需要历史数据，暂时用0）
        
        Returns:
            pd.DataFrame: 添加了质量评分的数据
        """
        weights = config.QUALITY_SCORE_WEIGHTS
        
        # 1. 播放吸引力分（播放量归一化）
        play_max = self.df['play'].max()
        play_score = (self.df['play'] / play_max * 100) if play_max > 0 else 0
        
        # 2. 内容质量分（直接使用互动率）
        engagement_score = self.df['engagement_rate']
        
        # 3. 传播力分（分享率 + 评论率的综合）
        spread_score = (self.df['share_rate'] + self.df['comment_rate']) * 2
        spread_score = spread_score.clip(0, 100)  # 限制在0-100
        
        # 4. 持久性分（暂时设为0，未来可以加入历史数据分析）
        duration_score = 0
        
        # 加权计算总分
        self.df['quality_score'] = (
            play_score * weights['play_score'] +
            engagement_score * weights['engagement_score'] +
            spread_score * weights['spread_score'] +
            duration_score * weights['duration_score']
        ).round(1)
        
        print(f"✓ 质量评分计算完成")
        print(f"  平均质量分：{self.df['quality_score'].mean():.1f}")
        print(f"  最高质量分：{self.df['quality_score'].max():.1f}")
        
        return self.df
    
    def get_top_videos(self, metric: str = 'play', n: int = 10) -> pd.DataFrame:
        """
        获取指定指标的TOP视频
        
        Args:
            metric: 排序指标（play, quality_score, engagement_rate等）
            n: 返回前N个
            
        Returns:
            pd.DataFrame: TOP视频数据
        """
        if metric not in self.df.columns:
            print(f"✗ 错误：指标 '{metric}' 不存在")
            return pd.DataFrame()
        
        top_videos = self.df.nlargest(n, metric)[
            ['title', 'play', 'engagement_rate', 'quality_score', 'content_type', 'created_date']
        ]
        
        return top_videos
    
    def get_hidden_gems(self, quality_threshold: float = 60, play_threshold: float = None) -> pd.DataFrame:
        """
        发现"遗珠"视频
        
        遗珠定义：高质量但低播放量的视频
        
        Args:
            quality_threshold: 质量分阈值（默认60分以上）
            play_threshold: 播放量阈值（默认为中位数）
            
        Returns:
            pd.DataFrame: 遗珠视频列表
        """
        if play_threshold is None:
            play_threshold = self.df['play'].median()
        
        hidden_gems = self.df[
            (self.df['quality_score'] >= quality_threshold) &
            (self.df['play'] < play_threshold)
        ].sort_values('quality_score', ascending=False)
        
        print(f"✓ 发现 {len(hidden_gems)} 个遗珠视频")
        
        return hidden_gems[['title', 'play', 'quality_score', 'engagement_rate', 'content_type']]
    
    def analyze_by_content_type(self) -> Dict[str, Dict]:
        """
        按内容类型分析表现
        
        Returns:
            Dict: 各内容类型的统计数据
        """
        results = {}
        
        for content_type in self.df['content_type'].unique():
            type_df = self.df[self.df['content_type'] == content_type]
            
            results[content_type] = {
                'count': len(type_df),
                'avg_play': type_df['play'].mean(),
                'median_play': type_df['play'].median(),
                'avg_engagement_rate': type_df['engagement_rate'].mean(),
                'avg_quality_score': type_df['quality_score'].mean(),
                'total_play': type_df['play'].sum(),
                'avg_length': type_df['length'].mean(),
                'avg_roi': type_df['roi'].mean()
            }
        
        return results
    
    def analyze_by_length_category(self) -> Dict[str, Dict]:
        """
        按视频时长分类分析表现
        
        Returns:
            Dict: 各时长类别的统计数据
        """
        results = {}
        
        for length_cat in self.df['length_category'].cat.categories:
            cat_df = self.df[self.df['length_category'] == length_cat]
            
            if len(cat_df) == 0:
                continue
            
            results[length_cat] = {
                'count': len(cat_df),
                'avg_play': cat_df['play'].mean(),
                'median_play': cat_df['play'].median(),
                'avg_engagement_rate': cat_df['engagement_rate'].mean(),
                'avg_quality_score': cat_df['quality_score'].mean(),
                'avg_roi': cat_df['roi'].mean()
            }
        
        return results
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        计算关键指标的相关性矩阵
        
        分析哪些指标之间存在相关关系
        
        Returns:
            pd.DataFrame: 相关性矩阵
        """
        # 选择需要分析相关性的指标
        correlation_columns = [
            'play', 'like', 'coin', 'favorite', 'share', 'comment',
            'length', 'engagement_rate', 'quality_score', 'roi'
        ]
        
        # 只保留存在的列
        available_columns = [col for col in correlation_columns if col in self.df.columns]
        
        # 计算相关性
        corr_matrix = self.df[available_columns].corr()
        
        return corr_matrix
    
    def get_performance_by_time(self) -> Dict:
        """
        按时间维度分析表现
        
        Returns:
            Dict: 时间维度的统计数据
        """
        results = {
            'by_year_month': self.df.groupby('year_month').agg({
                'bvid': 'count',
                'play': 'mean',
                'engagement_rate': 'mean',
                'quality_score': 'mean'
            }).to_dict('index'),
            
            'by_weekday': self.df.groupby('weekday').agg({
                'bvid': 'count',
                'play': 'mean',
                'engagement_rate': 'mean'
            }).to_dict('index'),
            
            'weekend_vs_weekday': {
                'weekend': {
                    'count': len(self.df[self.df['is_weekend']]),
                    'avg_play': self.df[self.df['is_weekend']]['play'].mean(),
                    'avg_engagement': self.df[self.df['is_weekend']]['engagement_rate'].mean()
                },
                'weekday': {
                    'count': len(self.df[~self.df['is_weekend']]),
                    'avg_play': self.df[~self.df['is_weekend']]['play'].mean(),
                    'avg_engagement': self.df[~self.df['is_weekend']]['engagement_rate'].mean()
                }
            }
        }
        
        return results
    
    def calculate_consistency_metrics(self) -> Dict:
        """
        计算内容稳定性指标
        
        用于评估账号的运营健康度
        
        Returns:
            Dict: 稳定性指标
        """
        metrics = {
            # 播放量波动系数（变异系数）
            'play_variation': (self.df['play'].std() / self.df['play'].mean() * 100) if self.df['play'].mean() > 0 else 0,
            
            # 互动率波动系数
            'engagement_variation': (self.df['engagement_rate'].std() / self.df['engagement_rate'].mean() * 100) 
                                    if self.df['engagement_rate'].mean() > 0 else 0,
            
            # 内容类型多样性（类型数量 / 总视频数）
            'content_diversity': len(self.df['content_type'].unique()) / len(self.df) * 100,
            
            # 发布频率稳定性（每月发布数量的标准差）
            'publish_frequency_std': self.df.groupby('year_month').size().std(),
            
            # 平均发布间隔（天）
            'avg_publish_interval': self.df['created_date'].diff().dt.days.mean()
        }
        
        return metrics
    
    def generate_insights(self) -> Dict:
        """
        生成数据洞察
        
        综合各类指标，生成关键发现
        
        Returns:
            Dict: 数据洞察报告
        """
        insights = {
            'best_performing': {
                'video': self.df.nlargest(1, 'quality_score').iloc[0].to_dict(),
                'content_type': max(
                    self.analyze_by_content_type().items(),
                    key=lambda x: x[1]['avg_quality_score']
                )[0],
                'length_category': max(
                    self.analyze_by_length_category().items(),
                    key=lambda x: x[1]['avg_quality_score']
                )[0]
            },
            'improvement_areas': {
                'low_engagement_videos': len(self.df[self.df['engagement_rate'] < 3]),
                'underperforming_content': self.df.nsmallest(5, 'quality_score')['content_type'].value_counts().to_dict()
            },
            'strengths': {
                'viral_video_rate': (self.df['is_viral'].sum() / len(self.df) * 100),
                'avg_quality_score': self.df['quality_score'].mean(),
                'avg_engagement_rate': self.df['engagement_rate'].mean()
            },
            'consistency': self.calculate_consistency_metrics()
        }
        
        return insights


# ==================== 使用示例 ====================
if __name__ == "__main__":
    from data_loader import DataLoader
    from feature_engineer import FeatureEngineer
    
    # 加载数据并进行特征工程
    data_file = Path(__file__).parent.parent.parent / "JSON_SAVE" / "analytics_SAVE.json"
    loader = DataLoader(data_file)
    df = loader.load_and_process()
    
    if df is not None:
        engineer = FeatureEngineer(df)
        df_engineered = engineer.engineer_all_features()
        
        # 计算指标
        calculator = MetricsCalculator(df_engineered)
        df_with_scores = calculator.calculate_quality_score()
        
        print("\n质量评分TOP5：")
        print(calculator.get_top_videos('quality_score', 5))
        
        print("\n遗珠视频：")
        print(calculator.get_hidden_gems())
        
        print("\n内容类型分析：")
        content_analysis = calculator.analyze_by_content_type()
        for content_type, stats in content_analysis.items():
            print(f"  {content_type}: 平均播放{stats['avg_play']:.0f}, 质量分{stats['avg_quality_score']:.1f}")
