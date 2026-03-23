"""
使用示例：演示如何单独使用各个模块
"""

from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
from bilibili_analyzer.analyzers import QualityScorer, ContentAdvisor
from bilibili_analyzer.visualizers import ReportGenerator


# ==================== 示例1：只做数据加载和基础分析 ====================
def example_basic_analysis():
    """
    示例1：最基础的使用方式
    """
    print("\n" + "="*60)
    print("示例1：基础数据加载和分析")
    print("="*60 + "\n")
    
    # 加载数据
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        # 查看基本信息
        print(f"视频总数：{len(df)}")
        print(f"平均播放量：{df['play'].mean():.0f}")
        print(f"最高播放量：{df['play'].max()}")
        print(f"\n播放量TOP3：")
        print(df.nlargest(3, 'play')[['title', 'play']])


# ==================== 示例2：只使用质量评分系统 ====================
def example_quality_scoring_only():
    """
    示例2：只使用质量评分功能
    """
    print("\n" + "="*60)
    print("示例2：质量评分分析")
    print("="*60 + "\n")
    
    # 数据准备
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        # 特征工程
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        # 计算质量分
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 生成质量报告
        scorer = QualityScorer(df)
        scorer.print_quality_report()
        
        # 导出质量评分数据（可选）
        # scorer.export_quality_scores('output/quality_scores.xlsx')


# ==================== 示例3：只使用内容决策系统 ====================
def example_content_advisor_only():
    """
    示例3：只使用内容决策功能
    """
    print("\n" + "="*60)
    print("示例3：内容决策分析")
    print("="*60 + "\n")
    
    # 数据准备
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        # 特征工程
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        # 计算质量分
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 生成内容决策报告
        advisor = ContentAdvisor(df)
        advisor.print_content_advisor_report()
        
        # 获取推荐建议
        recommendations = advisor.generate_recommendations(top_n=3)
        print("\n【推荐建议】")
        for rec in recommendations:
            print(f"\n{rec['rank']}. {rec['content']}")
            print(f"   理由：{rec['reason']}")


# ==================== 示例4：只生成图表 ====================
def example_generate_charts_only():
    """
    示例4：只生成可视化图表
    """
    print("\n" + "="*60)
    print("示例4：生成图表")
    print("="*60 + "\n")
    
    # 数据准备
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 生成所有图表
        generator = ReportGenerator(df)
        generator.generate_all_charts()


# ==================== 示例5：自定义分析 ====================
def example_custom_analysis():
    """
    示例5：自定义分析
    根据特定需求进行定制化分析
    """
    print("\n" + "="*60)
    print("示例5：自定义分析")
    print("="*60 + "\n")
    
    # 数据准备
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 自定义分析1：找出最需要改进的视频
        print("【需要改进的视频】")
        low_quality = df[df['quality_score'] < 40].sort_values('play', ascending=False)
        print(f"共有 {len(low_quality)} 个低质量视频")
        if len(low_quality) > 0:
            print("\n播放量最高的低质量视频（优先改进）：")
            print(low_quality.head(3)[['title', 'play', 'quality_score', 'content_type']])
        
        # 自定义分析2：分析周末vs工作日的表现
        print("\n【周末 vs 工作日表现】")
        weekend_avg = df[df['is_weekend']]['play'].mean()
        weekday_avg = df[~df['is_weekend']]['play'].mean()
        print(f"周末平均播放：{weekend_avg:.0f}")
        print(f"工作日平均播放：{weekday_avg:.0f}")
        print(f"差异：{(weekend_avg - weekday_avg) / weekday_avg * 100:+.1f}%")
        
        # 自定义分析3：找出最佳发布时间段
        print("\n【发布时间分析】")
        monthly_stats = df.groupby('year_month').agg({
            'bvid': 'count',
            'play': 'mean',
            'quality_score': 'mean'
        })
        monthly_stats.columns = ['发布数', '平均播放', '平均质量分']
        print(monthly_stats)


# ==================== 示例6：对比两个时间段 ====================
def example_time_period_comparison():
    """
    示例6：对比不同时间段的表现
    """
    print("\n" + "="*60)
    print("示例6：时间段对比分析")
    print("="*60 + "\n")
    
    # 数据准备
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is not None:
        engineer = FeatureEngineer(df)
        df = engineer.engineer_all_features()
        
        calculator = MetricsCalculator(df)
        df = calculator.calculate_quality_score()
        
        # 将数据分为前半段和后半段
        mid_date = df['created_date'].quantile(0.5)
        
        early_period = df[df['created_date'] < mid_date]
        late_period = df[df['created_date'] >= mid_date]
        
        print(f"早期时间段（{len(early_period)}个视频）：")
        print(f"  平均播放：{early_period['play'].mean():.0f}")
        print(f"  平均质量分：{early_period['quality_score'].mean():.1f}")
        print(f"  平均互动率：{early_period['engagement_rate'].mean():.2f}%")
        
        print(f"\n近期时间段（{len(late_period)}个视频）：")
        print(f"  平均播放：{late_period['play'].mean():.0f}")
        print(f"  平均质量分：{late_period['quality_score'].mean():.1f}")
        print(f"  平均互动率：{late_period['engagement_rate'].mean():.2f}%")
        
        # 计算增长率
        play_growth = (late_period['play'].mean() - early_period['play'].mean()) / early_period['play'].mean() * 100
        quality_growth = late_period['quality_score'].mean() - early_period['quality_score'].mean()
        
        print(f"\n【变化趋势】")
        print(f"  播放量增长：{play_growth:+.1f}%")
        print(f"  质量分变化：{quality_growth:+.1f}分")


# ==================== 主菜单 ====================
def main():
    """
    主菜单：选择要运行的示例
    """
    print("\n" + "="*80)
    print("🎓 B站UP主数据分析工具 - 使用示例".center(80))
    print("="*80)
    
    examples = {
        '1': ('基础数据加载和分析', example_basic_analysis),
        '2': ('质量评分分析', example_quality_scoring_only),
        '3': ('内容决策分析', example_content_advisor_only),
        '4': ('生成可视化图表', example_generate_charts_only),
        '5': ('自定义分析', example_custom_analysis),
        '6': ('时间段对比分析', example_time_period_comparison),
        '0': ('运行所有示例', None)
    }
    
    print("\n请选择要运行的示例：\n")
    for key, (name, _) in examples.items():
        print(f"  [{key}] {name}")
    
    choice = input("\n请输入选项（默认运行示例1）：").strip() or '1'
    
    if choice == '0':
        # 运行所有示例
        for key, (_, func) in examples.items():
            if key != '0' and func is not None:
                func()
                input("\n按回车继续...")
    elif choice in examples and examples[choice][1] is not None:
        examples[choice][1]()
    else:
        print("无效选项，运行示例1...")
        example_basic_analysis()


if __name__ == "__main__":
    main()
