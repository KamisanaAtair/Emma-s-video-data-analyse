"""
主运行脚本
整合所有功能,一键完成数据分析和报告生成
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config
from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
from bilibili_analyzer.analyzers import QualityScorer, ContentAdvisor
from bilibili_analyzer.visualizers import ReportGenerator


def main():
    """
    主函数：执行完整的数据分析流程
    """
    print("\n" + "="*80)
    print("🎬 B站UP主数据分析工具 v1.0".center(80))
    print("="*80 + "\n")
    
    # ==================== 第1步：数据加载 ====================
    print("【步骤1/6】数据加载...")
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is None:
        print("✗ 数据加载失败，程序终止")
        return
    
    # ==================== 第2步：特征工程 ====================
    print("\n【步骤2/6】特征工程...")
    engineer = FeatureEngineer(df)
    df = engineer.engineer_all_features()
    
    # ==================== 第3步：计算指标 ====================
    print("\n【步骤3/6】计算分析指标...")
    calculator = MetricsCalculator(df)
    df = calculator.calculate_quality_score()
    
    print(f"✓ 数据处理完成！当前数据包含 {len(df)} 个视频，{len(df.columns)} 个特征")
    
    # ==================== 第4步：功能B1 - 质量评分分析 ====================
    print("\n【步骤4/6】功能B1：视频质量评分分析...")
    scorer = QualityScorer(df)
    scorer.print_quality_report()
    
    # ==================== 第5步：功能B2 - 内容选择决策 ====================
    print("\n【步骤5/6】功能B2：内容选择决策分析...")
    advisor = ContentAdvisor(df)
    advisor.print_content_advisor_report()
    
    # ==================== 第6步：生成可视化报告 ====================
    print("\n【步骤6/6】生成可视化图表...")
    generator = ReportGenerator(df)
    generator.generate_all_charts()
    
    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("🎉 分析完成！".center(80))
    print("="*80)
    print(f"\n📊 图表保存位置：{config.FIGURES_DIR}")
    print(f"   - 质量评分图表：{config.FIGURES_DIR / 'quality'}")
    print(f"   - 内容决策图表：{config.FIGURES_DIR / 'content'}")
    print("\n" + "="*80 + "\n")


def quick_analysis():
    """
    快速分析模式：只输出核心结论，不生成详细报告
    """
    print("\n【快速分析模式】\n")
    
    # 加载数据
    loader = DataLoader(config.ANALYTICS_DATA_FILE)
    df = loader.load_and_process()
    
    if df is None:
        return
    
    # 特征工程
    engineer = FeatureEngineer(df)
    df = engineer.engineer_all_features()
    
    # 计算指标
    calculator = MetricsCalculator(df)
    df = calculator.calculate_quality_score()
    
    # 输出核心结论
    print("\n" + "="*60)
    print("📋 核心结论".center(60))
    print("="*60)
    
    # 1. 整体表现
    print(f"\n【整体表现】")
    print(f"  • 平均播放量：{df['play'].mean():.0f}")
    print(f"  • 平均质量分：{df['quality_score'].mean():.1f} / 100")
    print(f"  • 平均互动率：{df['engagement_rate'].mean():.2f}%")
    print(f"  • 爆款视频率：{df['is_viral'].sum() / len(df) * 100:.1f}%")
    
    # 2. 最佳内容类型
    best_type = df.groupby('content_type')['quality_score'].mean().idxmax()
    best_type_stats = df[df['content_type'] == best_type]
    print(f"\n【最佳内容类型】")
    print(f"  • 类型：{best_type}")
    print(f"  • 平均播放：{best_type_stats['play'].mean():.0f}")
    print(f"  • 平均质量分：{best_type_stats['quality_score'].mean():.1f}")
    
    # 3. TOP3视频
    print(f"\n【质量评分TOP3】")
    top3 = df.nlargest(3, 'quality_score')
    for idx, row in top3.iterrows():
        print(f"  {idx+1}. {row['title']}")
        print(f"     播放：{row['play']:,} | 质量分：{row['quality_score']:.1f}")
    
    # 4. 内容建议
    advisor = ContentAdvisor(df)
    recommendations = advisor.generate_recommendations(top_n=3)
    print(f"\n【内容推荐】")
    for rec in recommendations[:3]:
        print(f"  • {rec['content']}: {rec['reason']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # 快速模式
        quick_analysis()
    else:
        # 完整模式
        main()
