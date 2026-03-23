"""
报告生成器
整合所有分析结果和图表,生成完整的分析报告
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config
from .base_visualizer import BaseVisualizer


class ReportGenerator:
    """
    报告生成器
    
    功能：
    1. 为功能B1（质量评分）生成图表
    2. 为功能B2（内容决策）生成图表
    3. 生成综合分析报告
    """
    
    def __init__(self, df: pd.DataFrame, output_dir: Path = None):
        """
        初始化报告生成器
        
        Args:
            df: 完整的数据DataFrame
            output_dir: 输出目录
        """
        self.df = df
        self.visualizer = BaseVisualizer(output_dir)
        
    # ==================== 功能B1：质量评分系统图表 ====================
    
    def plot_quality_score_distribution(self) -> plt.Figure:
        """
        图B1-1：质量评分分布直方图
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(self.df['quality_score'], bins=20, 
               color=config.COLOR_PALETTE['primary'], 
               edgecolor='black', alpha=0.7)
        
        # 添加平均线
        mean_score = self.df['quality_score'].mean()
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2,
                  label=f'平均分: {mean_score:.1f}')
        
        ax.set_title('视频质量评分分布', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('质量评分', fontsize=12)
        ax.set_ylabel('视频数量', fontsize=12)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B1-1_quality_score_distribution', 'quality')
        return fig
    
    def plot_quality_vs_play_scatter(self) -> plt.Figure:
        """
        图B1-2：质量分 vs 播放量散点图（发现遗珠）
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制散点
        scatter = ax.scatter(self.df['play'], self.df['quality_score'],
                           s=100, alpha=0.6, 
                           c=self.df['quality_score'],
                           cmap='RdYlGn', edgecolors='black', linewidth=0.5)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('质量评分', fontsize=10)
        
        # 标注关键点（高质量低播放 = 遗珠）
        median_play = self.df['play'].median()
        hidden_gems = self.df[
            (self.df['quality_score'] >= 60) & 
            (self.df['play'] < median_play)
        ]
        
        # 标注遗珠视频
        for idx, row in hidden_gems.iterrows():
            ax.annotate(row['title'][:20], 
                       (row['play'], row['quality_score']),
                       fontsize=8, alpha=0.7,
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # 添加参考线
        ax.axhline(60, color='red', linestyle='--', alpha=0.5, label='高质量线(60分)')
        ax.axvline(median_play, color='blue', linestyle='--', alpha=0.5, label=f'播放中位数({median_play:.0f})')
        
        ax.set_title('视频质量分 vs 播放量（遗珠识别）', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('播放量', fontsize=12)
        ax.set_ylabel('质量评分', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B1-2_quality_vs_play_scatter', 'quality')
        return fig
    
    def plot_quality_radar(self) -> plt.Figure:
        """
        图B1-3：TOP3视频质量维度雷达图
        """
        # 选择TOP3视频
        top3 = self.df.nlargest(3, 'quality_score')
        
        # 雷达图需要的维度
        categories = ['播放量\n(归一化)', '互动率', '点赞率', '投币率', '收藏率']
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        # 为每个视频绘制雷达图
        colors = [config.COLOR_PALETTE['primary'], 
                 config.COLOR_PALETTE['secondary'],
                 config.COLOR_PALETTE['success']]
        
        for idx, (_, video) in enumerate(top3.iterrows()):
            # 归一化数据到0-100
            values = [
                video['play'] / self.df['play'].max() * 100,
                video['engagement_rate'],
                video['like_rate'],
                video['coin_rate'],
                video['favorite_rate']
            ]
            values += values[:1]  # 闭合图形
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=video['title'][:20], color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_title('TOP3视频质量维度对比', fontsize=16, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B1-3_quality_radar', 'quality')
        return fig
    
    # ==================== 功能B2：内容选择决策图表 ====================
    
    def plot_content_type_performance(self) -> plt.Figure:
        """
        图B2-1：内容类型表现对比（分组柱状图）
        """
        # 按内容类型统计
        type_stats = self.df.groupby('content_type').agg({
            'play': 'mean',
            'engagement_rate': 'mean',
            'quality_score': 'mean'
        }).round(1)
        
        type_stats.columns = ['平均播放量', '平均互动率', '平均质量分']
        
        # 归一化到0-100以便对比
        type_stats_normalized = type_stats.copy()
        type_stats_normalized['平均播放量'] = type_stats_normalized['平均播放量'] / type_stats_normalized['平均播放量'].max() * 100
        
        fig = self.visualizer.plot_grouped_bar(
            type_stats_normalized,
            '各内容类型表现对比',
            '内容类型',
            '得分（归一化）'
        )
        
        # 保存
        self.visualizer.save_figure(fig, 'B2-1_content_type_performance', 'content')
        return fig
    
    def plot_content_type_pie(self) -> plt.Figure:
        """
        图B2-2：内容类型分布饼图
        """
        type_counts = self.df['content_type'].value_counts()
        
        fig = self.visualizer.plot_pie(
            type_counts,
            '视频内容类型分布'
        )
        
        # 保存
        self.visualizer.save_figure(fig, 'B2-2_content_type_pie', 'content')
        return fig
    
    def plot_length_vs_performance(self) -> plt.Figure:
        """
        图B2-3：视频时长 vs 表现（散点图 + 趋势线）
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制散点
        scatter = ax.scatter(self.df['length_minutes'], self.df['quality_score'],
                           s=self.df['play']/10,  # 大小表示播放量
                           alpha=0.6, 
                           c=self.df['engagement_rate'],
                           cmap='viridis', edgecolors='black', linewidth=0.5)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('互动率 (%)', fontsize=10)
        
        # 添加趋势线
        z = np.polyfit(self.df['length_minutes'], self.df['quality_score'], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(self.df['length_minutes'].min(), self.df['length_minutes'].max(), 100)
        ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label='趋势线')
        
        ax.set_title('视频时长 vs 质量表现', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('视频时长（分钟）', fontsize=12)
        ax.set_ylabel('质量评分', fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)
        
        # 添加说明文字
        ax.text(0.02, 0.98, '※ 气泡大小代表播放量', 
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B2-3_length_vs_performance', 'content')
        return fig
    
    def plot_roi_ranking(self) -> plt.Figure:
        """
        图B2-4：内容ROI排行榜
        """
        # 按内容类型计算平均ROI
        roi_stats = self.df.groupby('content_type')['roi'].mean().sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        bars = ax.barh(range(len(roi_stats)), roi_stats.values,
                      color=config.COLOR_PALETTE['success'], 
                      edgecolor='black', alpha=0.7)
        
        # 为每个柱子添加数值标签
        for i, (idx, value) in enumerate(roi_stats.items()):
            ax.text(value, i, f' {value:.1f}', 
                   va='center', fontsize=10, fontweight='bold')
        
        ax.set_yticks(range(len(roi_stats)))
        ax.set_yticklabels(roi_stats.index)
        ax.set_xlabel('ROI（播放量/时长）', fontsize=12)
        ax.set_title('各内容类型ROI排行榜', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B2-4_roi_ranking', 'content')
        return fig
    
    def plot_title_feature_effect(self) -> plt.Figure:
        """
        图B2-5：标题特征影响对比
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. 【】标签效果
        bracket_stats = self.df.groupby('has_bracket_tag')['play'].mean()
        bracket_labels = ['不使用【】', '使用【】']
        
        bars1 = ax1.bar(bracket_labels, bracket_stats.values,
                       color=[config.COLOR_PALETTE['neutral'], config.COLOR_PALETTE['primary']],
                       edgecolor='black', alpha=0.7)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax1.set_title('【】标签对播放量的影响', fontsize=14, fontweight='bold')
        ax1.set_ylabel('平均播放量', fontsize=11)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. 表情符号效果
        emoji_stats = self.df.groupby('has_emoji')['play'].mean()
        emoji_labels = ['不使用表情', '使用表情']
        
        bars2 = ax2.bar(emoji_labels, emoji_stats.values,
                       color=[config.COLOR_PALETTE['neutral'], config.COLOR_PALETTE['secondary']],
                       edgecolor='black', alpha=0.7)
        
        # 添加数值标签
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax2.set_title('表情符号对播放量的影响', fontsize=14, fontweight='bold')
        ax2.set_ylabel('平均播放量', fontsize=11)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle('标题特征效果分析', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # 保存
        self.visualizer.save_figure(fig, 'B2-5_title_feature_effect', 'content')
        return fig
    
    # ==================== 综合报告生成 ====================
    
    def generate_all_charts(self):
        """
        生成所有图表
        """
        print("\n" + "="*80)
        print("📈 开始生成图表...".center(80))
        print("="*80 + "\n")
        
        # 功能B1：质量评分系统图表
        print("【功能B1：质量评分系统】")
        self.plot_quality_score_distribution()
        plt.close()
        
        self.plot_quality_vs_play_scatter()
        plt.close()
        
        self.plot_quality_radar()
        plt.close()
        
        # 功能B2：内容选择决策图表
        print("\n【功能B2：内容选择决策】")
        self.plot_content_type_performance()
        plt.close()
        
        self.plot_content_type_pie()
        plt.close()
        
        self.plot_length_vs_performance()
        plt.close()
        
        self.plot_roi_ranking()
        plt.close()
        
        self.plot_title_feature_effect()
        plt.close()
        
        print("\n" + "="*80)
        print("✓ 所有图表生成完成！".center(80))
        print(f"图表保存位置：{self.visualizer.output_dir}".center(80))
        print("="*80 + "\n")


# ==================== 使用示例 ====================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加路径
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
    
    # 完整流程
    data_file = Path(__file__).parent.parent.parent / "JSON_SAVE" / "analytics_SAVE.json"
    
    # 1. 加载和处理数据
    loader = DataLoader(data_file)
    df = loader.load_and_process()
    
    if df is not None:
        # 2. 特征工程
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        # 3. 计算质量评分
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 4. 生成所有图表
        generator = ReportGenerator(df)
        generator.generate_all_charts()
