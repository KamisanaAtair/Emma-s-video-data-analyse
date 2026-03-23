"""
功能B2：内容选择决策树
基于历史数据，为UP主推荐下一个视频应该做什么内容
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config


class ContentAdvisor:
    """
    内容选择决策器
    
    功能：
    1. 分析各类内容的表现
    2. 推荐最佳内容方向
    3. 识别内容空白区
    4. 提供具体的内容建议
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化内容决策器
        
        Args:
            df: 包含完整特征的DataFrame
        """
        self.df = df
        self.content_analysis = None
        
    def analyze_content_performance(self) -> Dict:
        """
        全面分析各类内容的表现
        
        Returns:
            Dict: 内容表现分析报告
        """
        analysis = {
            'by_content_type': self._analyze_by_content_type(),
            'by_length': self._analyze_by_length(),
            'by_title_features': self._analyze_title_features(),
            'content_gaps': self._identify_content_gaps(),
            'best_combinations': self._find_best_combinations()
        }
        
        self.content_analysis = analysis
        return analysis
    
    def _analyze_by_content_type(self) -> Dict:
        """
        按内容类型分析表现
        """
        type_stats = {}
        
        for content_type in self.df['content_type'].unique():
            type_df = self.df[self.df['content_type'] == content_type]
            
            type_stats[content_type] = {
                'count': len(type_df),
                'avg_play': type_df['play'].mean(),
                'median_play': type_df['play'].median(),
                'max_play': type_df['play'].max(),
                'avg_engagement': type_df['engagement_rate'].mean(),
                'avg_quality': type_df['quality_score'].mean(),
                'total_play': type_df['play'].sum(),
                'avg_roi': type_df['roi'].mean(),
                'success_rate': len(type_df[type_df['is_viral']]) / len(type_df) * 100 if len(type_df) > 0 else 0,
                'avg_length': type_df['length_minutes'].mean()
            }
        
        # 按综合得分排序（质量分 + ROI）
        type_stats = dict(sorted(
            type_stats.items(),
            key=lambda x: x[1]['avg_quality'] + x[1]['avg_roi'] / 100,
            reverse=True
        ))
        
        return type_stats
    
    def _analyze_by_length(self) -> Dict:
        """
        按视频时长分析表现
        """
        length_stats = {}
        
        for length_cat in self.df['length_category'].cat.categories:
            cat_df = self.df[self.df['length_category'] == length_cat]
            
            if len(cat_df) == 0:
                continue
            
            length_stats[length_cat] = {
                'count': len(cat_df),
                'avg_play': cat_df['play'].mean(),
                'avg_engagement': cat_df['engagement_rate'].mean(),
                'avg_quality': cat_df['quality_score'].mean(),
                'avg_roi': cat_df['roi'].mean(),
                'success_rate': len(cat_df[cat_df['is_viral']]) / len(cat_df) * 100
            }
        
        return length_stats
    
    def _analyze_title_features(self) -> Dict:
        """
        分析标题特征的影响
        """
        # 使用标签 vs 不使用标签
        with_bracket = self.df[self.df['has_bracket_tag']]
        without_bracket = self.df[~self.df['has_bracket_tag']]
        
        # 使用表情 vs 不使用表情
        with_emoji = self.df[self.df['has_emoji']]
        without_emoji = self.df[~self.df['has_emoji']]
        
        # 标题长度分析
        # 将标题分为短中长三类
        title_length_bins = [0, 15, 30, float('inf')]
        title_length_labels = ['短标题(<15字)', '中等标题(15-30字)', '长标题(>30字)']
        self.df['title_length_category'] = pd.cut(
            self.df['title_length'],
            bins=title_length_bins,
            labels=title_length_labels
        )
        
        return {
            'bracket_tag_effect': {
                'with_bracket': {
                    'count': len(with_bracket),
                    'avg_play': with_bracket['play'].mean() if len(with_bracket) > 0 else 0,
                    'avg_engagement': with_bracket['engagement_rate'].mean() if len(with_bracket) > 0 else 0
                },
                'without_bracket': {
                    'count': len(without_bracket),
                    'avg_play': without_bracket['play'].mean() if len(without_bracket) > 0 else 0,
                    'avg_engagement': without_bracket['engagement_rate'].mean() if len(without_bracket) > 0 else 0
                }
            },
            'emoji_effect': {
                'with_emoji': {
                    'count': len(with_emoji),
                    'avg_play': with_emoji['play'].mean() if len(with_emoji) > 0 else 0,
                    'avg_engagement': with_emoji['engagement_rate'].mean() if len(with_emoji) > 0 else 0
                },
                'without_emoji': {
                    'count': len(without_emoji),
                    'avg_play': without_emoji['play'].mean() if len(without_emoji) > 0 else 0,
                    'avg_engagement': without_emoji['engagement_rate'].mean() if len(without_emoji) > 0 else 0
                }
            },
            'title_length_effect': self.df.groupby('title_length_category').agg({
                'play': 'mean',
                'engagement_rate': 'mean',
                'quality_score': 'mean'
            }).to_dict('index')
        }
    
    def _identify_content_gaps(self) -> Dict:
        """
        识别内容空白区
        
        找出：
        1. 做得少但表现好的类型
        2. 完全没做过的类型
        3. 有潜力的组合
        """
        gaps = {
            'underproduced_good_types': [],
            'potential_combinations': []
        }
        
        # 找出做得少但表现好的类型（数量 < 中位数 且 质量分 > 平均）
        type_stats = self._analyze_by_content_type()
        type_counts = [stats['count'] for stats in type_stats.values()]
        median_count = np.median(type_counts) if type_counts else 0
        avg_quality = self.df['quality_score'].mean()
        
        for content_type, stats in type_stats.items():
            if stats['count'] < median_count and stats['avg_quality'] > avg_quality:
                gaps['underproduced_good_types'].append({
                    'type': content_type,
                    'count': stats['count'],
                    'avg_quality': stats['avg_quality'],
                    'avg_play': stats['avg_play']
                })
        
        # 分析内容类型 × 时长的组合
        combination_stats = self.df.groupby(['content_type', 'length_category']).agg({
            'play': 'mean',
            'quality_score': 'mean',
            'bvid': 'count'
        }).reset_index()
        combination_stats.columns = ['content_type', 'length_category', 'avg_play', 'avg_quality', 'count']
        
        # 找出表现好但做得少的组合
        for _, row in combination_stats.iterrows():
            if row['count'] <= 2 and row['avg_quality'] > avg_quality:
                gaps['potential_combinations'].append({
                    'type': row['content_type'],
                    'length': row['length_category'],
                    'count': row['count'],
                    'avg_quality': row['avg_quality'],
                    'avg_play': row['avg_play']
                })
        
        return gaps
    
    def _find_best_combinations(self) -> List[Dict]:
        """
        找出表现最好的内容组合
        
        内容类型 × 视频时长 × 标题特征
        """
        combinations = []
        
        # 分析每种组合的表现
        for content_type in self.df['content_type'].unique():
            for length_cat in self.df['length_category'].cat.categories:
                combo_df = self.df[
                    (self.df['content_type'] == content_type) &
                    (self.df['length_category'] == length_cat)
                ]
                
                if len(combo_df) == 0:
                    continue
                
                combinations.append({
                    'content_type': content_type,
                    'length': length_cat,
                    'count': len(combo_df),
                    'avg_play': combo_df['play'].mean(),
                    'avg_quality': combo_df['quality_score'].mean(),
                    'avg_engagement': combo_df['engagement_rate'].mean(),
                    'success_rate': len(combo_df[combo_df['is_viral']]) / len(combo_df) * 100
                })
        
        # 按综合得分排序
        combinations.sort(
            key=lambda x: x['avg_quality'] * 0.5 + x['avg_play'] / 100 * 0.5,
            reverse=True
        )
        
        return combinations[:10]  # 返回TOP10
    
    def generate_recommendations(self, top_n: int = 3) -> List[Dict]:
        """
        生成内容推荐
        
        基于数据分析，给出TOP N的内容建议
        
        Args:
            top_n: 返回前N个推荐
            
        Returns:
            List[Dict]: 推荐列表
        """
        if self.content_analysis is None:
            self.analyze_content_performance()
        
        recommendations = []
        
        # 推荐1：表现最好的内容类型
        type_stats = self.content_analysis['by_content_type']
        best_types = list(type_stats.items())[:top_n]
        
        for rank, (content_type, stats) in enumerate(best_types, 1):
            recommendations.append({
                'rank': rank,
                'recommendation_type': '最佳内容类型',
                'content': content_type,
                'reason': f'平均质量分 {stats["avg_quality"]:.1f}，平均播放 {stats["avg_play"]:.0f}',
                'suggested_length': f'{stats["avg_length"]:.1f} 分钟',
                'expected_performance': {
                    'play': stats['avg_play'],
                    'engagement': stats['avg_engagement'],
                    'quality': stats['avg_quality']
                },
                'priority': '高' if rank == 1 else '中'
            })
        
        # 推荐2：潜力组合
        best_combos = self.content_analysis['best_combinations'][:2]
        for combo in best_combos:
            if combo['count'] >= 2:  # 至少有2个样本
                recommendations.append({
                    'rank': len(recommendations) + 1,
                    'recommendation_type': '最佳内容组合',
                    'content': f'{combo["content_type"]} ({combo["length"]})',
                    'reason': f'该组合平均质量分 {combo["avg_quality"]:.1f}，爆款率 {combo["success_rate"]:.1f}%',
                    'suggested_length': combo["length"],
                    'expected_performance': {
                        'play': combo['avg_play'],
                        'engagement': combo['avg_engagement'],
                        'quality': combo['avg_quality']
                    },
                    'priority': '中'
                })
        
        # 推荐3：内容空白区机会
        gaps = self.content_analysis['content_gaps']['underproduced_good_types']
        if gaps:
            gap = gaps[0]
            recommendations.append({
                'rank': len(recommendations) + 1,
                'recommendation_type': '潜力内容类型',
                'content': gap['type'],
                'reason': f'做得少但质量高（仅{gap["count"]}个视频，质量分{gap["avg_quality"]:.1f}）',
                'suggested_length': '参考历史最佳',
                'expected_performance': {
                    'play': gap['avg_play'],
                    'quality': gap['avg_quality']
                },
                'priority': '中'
            })
        
        return recommendations
    
    def print_content_advisor_report(self):
        """
        美化打印内容决策报告
        """
        if self.content_analysis is None:
            self.analyze_content_performance()
        
        print("\n" + "="*80)
        print("🎯 内容选择决策报告".center(80))
        print("="*80)
        
        # 1. 内容类型表现排行
        print("\n【内容类型表现排行】")
        type_stats = self.content_analysis['by_content_type']
        print(f"{'排名':<4} {'内容类型':<15} {'数量':<6} {'平均播放':<10} {'质量分':<8} {'ROI':<8} {'爆款率':<8}")
        print("-" * 80)
        for rank, (content_type, stats) in enumerate(list(type_stats.items())[:5], 1):
            print(f"{rank:<4} {content_type:<15} {stats['count']:<6} "
                  f"{stats['avg_play']:<10.0f} {stats['avg_quality']:<8.1f} "
                  f"{stats['avg_roi']:<8.1f} {stats['success_rate']:<8.1f}%")
        
        # 2. 视频时长建议
        print("\n【视频时长建议】")
        length_stats = self.content_analysis['by_length']
        best_length = max(length_stats.items(), key=lambda x: x[1]['avg_quality'])
        print(f"  最佳时长：{best_length[0]}")
        print(f"  ├─ 平均播放：{best_length[1]['avg_play']:.0f}")
        print(f"  ├─ 平均质量分：{best_length[1]['avg_quality']:.1f}")
        print(f"  └─ 爆款率：{best_length[1]['success_rate']:.1f}%")
        
        # 3. 标题特征分析
        print("\n【标题特征影响】")
        title_features = self.content_analysis['by_title_features']
        
        bracket_effect = title_features['bracket_tag_effect']
        with_bracket = bracket_effect['with_bracket']
        without_bracket = bracket_effect['without_bracket']
        if with_bracket['count'] > 0 and without_bracket['count'] > 0:
            bracket_lift = (with_bracket['avg_play'] - without_bracket['avg_play']) / without_bracket['avg_play'] * 100
            print(f"  • 使用【】标签：平均播放 {with_bracket['avg_play']:.0f} ({bracket_lift:+.1f}% vs 不使用)")
        
        emoji_effect = title_features['emoji_effect']
        with_emoji = emoji_effect['with_emoji']
        without_emoji = emoji_effect['without_emoji']
        if with_emoji['count'] > 0 and without_emoji['count'] > 0:
            emoji_lift = (with_emoji['avg_play'] - without_emoji['avg_play']) / without_emoji['avg_play'] * 100
            print(f"  • 使用表情符号：平均播放 {with_emoji['avg_play']:.0f} ({emoji_lift:+.1f}% vs 不使用)")
        
        # 4. 最佳内容组合
        print("\n【最佳内容组合 TOP3】")
        best_combos = self.content_analysis['best_combinations'][:3]
        for rank, combo in enumerate(best_combos, 1):
            print(f"  {rank}. {combo['content_type']} × {combo['length']}")
            print(f"     质量分：{combo['avg_quality']:.1f} | 播放：{combo['avg_play']:.0f} | 样本数：{combo['count']}")
        
        # 5. 内容空白区
        print("\n【内容机会点】")
        gaps = self.content_analysis['content_gaps']
        
        if gaps['underproduced_good_types']:
            print("  • 做得少但表现好的类型：")
            for gap in gaps['underproduced_good_types'][:3]:
                print(f"    - {gap['type']}: 仅{gap['count']}个视频，但质量分{gap['avg_quality']:.1f}")
        else:
            print("  • 暂无明显的内容空白区")
        
        # 6. 推荐建议
        print("\n【内容推荐（按优先级）】")
        recommendations = self.generate_recommendations(top_n=5)
        for rec in recommendations:
            print(f"\n  推荐 {rec['rank']}：{rec['content']} [{rec['priority']}优先级]")
            print(f"  ├─ 类型：{rec['recommendation_type']}")
            print(f"  ├─ 理由：{rec['reason']}")
            print(f"  ├─ 建议时长：{rec['suggested_length']}")
            perf = rec['expected_performance']
            print(f"  └─ 预期表现：播放 {perf.get('play', 0):.0f}，质量分 {perf.get('quality', 0):.1f}")
        
        print("\n" + "="*80 + "\n")


# ==================== 使用示例 ====================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加路径
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
    
    # 完整流程演示
    data_file = Path(__file__).parent.parent.parent / "JSON_SAVE" / "analytics_SAVE.json"
    
    # 1. 加载数据
    loader = DataLoader(data_file)
    df = loader.load_and_process()
    
    if df is not None:
        # 2. 特征工程
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        # 3. 计算质量评分
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 4. 生成内容决策报告
        advisor = ContentAdvisor(df)
        advisor.print_content_advisor_report()
