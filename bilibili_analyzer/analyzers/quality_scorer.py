"""
功能B1：视频质量评分系统
对每个视频进行全方位质量评估，并给出具体的改进建议
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config


class QualityScorer:
    """
    视频质量评分系统
    
    功能：
    1. 计算综合质量评分
    2. 生成质量报告
    3. 识别高质量低曝光的"遗珠"视频
    4. 提供改进建议
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化质量评分系统
        
        Args:
            df: 包含质量评分的DataFrame
        """
        self.df = df
        self.quality_report = None
        
    def generate_quality_report(self) -> Dict:
        """
        生成完整的质量评估报告
        
        Returns:
            Dict: 质量评估报告
        """
        report = {
            'summary': self._get_quality_summary(),
            'top_quality_videos': self._get_top_quality_videos(),
            'hidden_gems': self._find_hidden_gems(),
            'quality_distribution': self._analyze_quality_distribution(),
            'quality_by_type': self._analyze_quality_by_type(),
            'improvement_recommendations': self._generate_recommendations()
        }
        
        self.quality_report = report
        return report
    
    def _get_quality_summary(self) -> Dict:
        """
        获取质量评分总体概况
        """
        summary = {
            'total_videos': len(self.df),
            'avg_quality_score': self.df['quality_score'].mean(),
            'median_quality_score': self.df['quality_score'].median(),
            'std_quality_score': self.df['quality_score'].std(),
            'high_quality_count': len(self.df[self.df['quality_score'] >= 70]),
            'medium_quality_count': len(self.df[(self.df['quality_score'] >= 40) & (self.df['quality_score'] < 70)]),
            'low_quality_count': len(self.df[self.df['quality_score'] < 40]),
            'high_quality_rate': len(self.df[self.df['quality_score'] >= 70]) / len(self.df) * 100
        }
        return summary
    
    def _get_top_quality_videos(self, n: int = 10) -> pd.DataFrame:
        """
        获取质量评分最高的视频
        """
        top_videos = self.df.nlargest(n, 'quality_score')[[
            'title', 'play', 'engagement_rate', 'quality_score', 
            'content_type', 'length_minutes', 'created_date'
        ]].copy()
        
        # 格式化日期
        top_videos['created_date'] = top_videos['created_date'].dt.strftime('%Y-%m-%d')
        
        return top_videos
    
    def _find_hidden_gems(self, quality_threshold: float = 60) -> pd.DataFrame:
        """
        发现遗珠视频（高质量但低播放量）
        
        Args:
            quality_threshold: 质量分阈值
        """
        # 使用中位数作为播放量的分界线
        play_median = self.df['play'].median()
        
        hidden_gems = self.df[
            (self.df['quality_score'] >= quality_threshold) &
            (self.df['play'] < play_median)
        ].sort_values('quality_score', ascending=False)
        
        if len(hidden_gems) > 0:
            return hidden_gems[[
                'title', 'play', 'engagement_rate', 'quality_score', 
                'content_type', 'created_date'
            ]].copy()
        else:
            return pd.DataFrame()
    
    def _analyze_quality_distribution(self) -> Dict:
        """
        分析质量分布情况
        """
        # 将质量分分为几个档次
        bins = [0, 40, 60, 80, 100]
        labels = ['低质量(<40)', '中等质量(40-60)', '良好质量(60-80)', '优秀质量(80-100)']
        
        self.df['quality_level'] = pd.cut(
            self.df['quality_score'],
            bins=bins,
            labels=labels,
            include_lowest=True
        )
        
        distribution = self.df['quality_level'].value_counts().to_dict()
        distribution_pct = (self.df['quality_level'].value_counts(normalize=True) * 100).to_dict()
        
        return {
            'counts': distribution,
            'percentages': distribution_pct
        }
    
    def _analyze_quality_by_type(self) -> Dict:
        """
        按内容类型分析质量
        """
        quality_by_type = {}
        
        for content_type in self.df['content_type'].unique():
            type_df = self.df[self.df['content_type'] == content_type]
            
            quality_by_type[content_type] = {
                'count': len(type_df),
                'avg_quality': type_df['quality_score'].mean(),
                'avg_play': type_df['play'].mean(),
                'avg_engagement': type_df['engagement_rate'].mean(),
                'high_quality_rate': len(type_df[type_df['quality_score'] >= 70]) / len(type_df) * 100 if len(type_df) > 0 else 0
            }
        
        # 按平均质量分排序
        quality_by_type = dict(sorted(
            quality_by_type.items(),
            key=lambda x: x[1]['avg_quality'],
            reverse=True
        ))
        
        return quality_by_type
    
    def _generate_recommendations(self) -> List[Dict]:
        """
        生成改进建议
        
        基于数据分析，提供可操作的改进建议
        """
        recommendations = []
        
        # 建议1：识别需要二次推广的遗珠视频
        hidden_gems = self._find_hidden_gems()
        if len(hidden_gems) > 0:
            recommendations.append({
                'type': '二次推广机会',
                'priority': '高',
                'description': f'发现 {len(hidden_gems)} 个高质量但低播放量的视频',
                'action': f'建议对这些视频进行二次推广或制作合集，标题：{hidden_gems.iloc[0]["title"]}',
                'expected_benefit': '可能带来额外的流量和曝光'
            })
        
        # 建议2：分析低质量视频的特点
        low_quality = self.df[self.df['quality_score'] < 40]
        if len(low_quality) > 0:
            common_issues = []
            
            # 检查是否互动率过低
            if low_quality['engagement_rate'].mean() < 3:
                common_issues.append('互动率偏低')
            
            # 检查是否播放量过低
            if low_quality['play'].mean() < self.df['play'].quantile(0.25):
                common_issues.append('播放量不足')
            
            recommendations.append({
                'type': '内容质量改进',
                'priority': '中',
                'description': f'有 {len(low_quality)} 个低质量视频',
                'action': f'主要问题：{", ".join(common_issues)}。建议优化内容质量和标题吸引力',
                'expected_benefit': '提升整体内容质量'
            })
        
        # 建议3：推荐最优内容类型
        quality_by_type = self._analyze_quality_by_type()
        best_type = list(quality_by_type.keys())[0]
        best_stats = quality_by_type[best_type]
        
        recommendations.append({
            'type': '内容方向建议',
            'priority': '高',
            'description': f'"{best_type}"类型视频表现最好',
            'action': f'平均质量分{best_stats["avg_quality"]:.1f}，平均播放量{best_stats["avg_play"]:.0f}。建议增加此类型内容的产出',
            'expected_benefit': '提升整体账号表现'
        })
        
        # 建议4：视频时长优化
        best_length = self.df.groupby('length_category')['quality_score'].mean().idxmax()
        recommendations.append({
            'type': '视频时长优化',
            'priority': '中',
            'description': f'"{best_length}"时长的视频质量分最高',
            'action': f'建议未来视频时长控制在此区间',
            'expected_benefit': '更好的内容质量和观看体验'
        })
        
        return recommendations
    
    def print_quality_report(self):
        """
        美化打印质量报告
        """
        if self.quality_report is None:
            self.generate_quality_report()
        
        report = self.quality_report
        
        print("\n" + "="*80)
        print("📊 视频质量评分报告".center(80))
        print("="*80)
        
        # 1. 总体概况
        summary = report['summary']
        print("\n【总体概况】")
        print(f"  • 视频总数：{summary['total_videos']}")
        print(f"  • 平均质量分：{summary['avg_quality_score']:.1f} / 100")
        print(f"  • 质量中位数：{summary['median_quality_score']:.1f}")
        print(f"  • 质量波动：±{summary['std_quality_score']:.1f}")
        print(f"  • 高质量视频：{summary['high_quality_count']} 个 ({summary['high_quality_rate']:.1f}%)")
        print(f"  • 中等质量视频：{summary['medium_quality_count']} 个")
        print(f"  • 低质量视频：{summary['low_quality_count']} 个")
        
        # 2. TOP质量视频
        print("\n【质量评分 TOP5】")
        top_videos = report['top_quality_videos'].head(5)
        for idx, row in top_videos.iterrows():
            print(f"  {idx+1}. {row['title'][:40]}")
            print(f"     质量分：{row['quality_score']:.1f} | 播放：{row['play']:,} | 互动率：{row['engagement_rate']:.2f}%")
        
        # 3. 遗珠视频
        hidden_gems = report['hidden_gems']
        if len(hidden_gems) > 0:
            print(f"\n【遗珠视频（高质量低播放）】共 {len(hidden_gems)} 个")
            for idx, row in hidden_gems.head(3).iterrows():
                print(f"  • {row['title'][:40]}")
                print(f"    质量分：{row['quality_score']:.1f} | 播放：{row['play']:,} | 互动率：{row['engagement_rate']:.2f}%")
        else:
            print("\n【遗珠视频】未发现明显的遗珠视频")
        
        # 4. 质量分布
        print("\n【质量分布】")
        dist = report['quality_distribution']['percentages']
        for level, pct in dist.items():
            bar_length = int(pct / 2)  # 每个字符代表2%
            bar = "█" * bar_length
            print(f"  {level:20s} {bar} {pct:.1f}%")
        
        # 5. 内容类型质量
        print("\n【各类型内容质量排行】")
        quality_by_type = report['quality_by_type']
        for idx, (content_type, stats) in enumerate(list(quality_by_type.items())[:5], 1):
            print(f"  {idx}. {content_type:15s} 质量分：{stats['avg_quality']:.1f} | 视频数：{stats['count']}")
        
        # 6. 改进建议
        print("\n【改进建议】")
        for idx, rec in enumerate(report['improvement_recommendations'], 1):
            print(f"\n  建议 {idx}：{rec['type']} [优先级：{rec['priority']}]")
            print(f"  ├─ 现状：{rec['description']}")
            print(f"  ├─ 行动：{rec['action']}")
            print(f"  └─ 预期收益：{rec['expected_benefit']}")
        
        print("\n" + "="*80 + "\n")
    
    def export_quality_scores(self, output_file: str):
        """
        导出质量评分数据
        
        Args:
            output_file: 输出文件路径
        """
        export_df = self.df[[
            'title', 'bvid', 'play', 'engagement_rate', 
            'quality_score', 'content_type', 'length_minutes', 'created_date'
        ]].sort_values('quality_score', ascending=False)
        
        export_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ 质量评分数据已导出到：{output_file}")


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
        
        # 4. 生成质量报告
        scorer = QualityScorer(df)
        scorer.print_quality_report()
