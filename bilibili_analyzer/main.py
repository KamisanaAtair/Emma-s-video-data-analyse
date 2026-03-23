"""
B站UP主数据分析工具 - 主程序
实现功能B1（视频质量评分系统）和B2（内容选择决策树）
"""

from pathlib import Path
from core.data_loader import DataLoader
from core.feature_engineer import FeatureEngineer
from analyzers.quality_scorer import QualityScorer
from analyzers.content_advisor import ContentAdvisor
from visualizers.report_generator import ReportGenerator
from config import config


def main():
    """主函数"""
    
    print("\n" + "🎬"*40)
    print("  B站UP主数据分析工具 v1.0")
    print("  功能: 视频质量评分 + 内容策略建议")
    print("🎬"*40 + "\n")
    
    # ==================== 1. 环境准备 ====================
    print("📦 Step 1: 准备环境...")
    
    # 配置matplotlib
    config.setup_matplotlib()
    
    # 确保输出目录存在
    config.ensure_dirs()
    
    print("✓ 环境准备完成\n")
    
    # ==================== 2. 加载数据 ====================
    print("📂 Step 2: 加载数据...")
    
    # 初始化数据加载器
    loader = DataLoader(config.ANALYTICS_DATA)
    
    # 加载并预处理数据
    df = loader.load_data()
    df = loader.preprocess_data()
    
    # 打印数据摘要
    loader.print_summary()
    
    # ==================== 3. 特征工程 ====================
    print("🔧 Step 3: 特征工程...")
    
    # 初始化特征工程器
    engineer = FeatureEngineer(df)
    
    # 添加所有特征
    df = engineer.add_all_features()
    
    # ==================== 4. 数据分析 ====================
    print("\n🔍 Step 4: 开始数据分析...")
    
    # 4.1 视频质量评分
    print("\n" + "-"*60)
    print("📊 功能B1: 视频质量评分系统")
    print("-"*60)
    
    quality_scorer = QualityScorer(df)
    df = quality_scorer.calculate_scores()
    
    # 打印质量分析报告
    quality_scorer.print_report()
    
    # 查看TOP5高质量视频
    print("\n【TOP 5 高质量视频详情】")
    top5 = quality_scorer.get_top_quality_videos(5)
    print(top5.to_string(index=False))
    
    # 查看遗珠视频
    print("\n【遗珠视频详情】")
    hidden_gems = quality_scorer.find_hidden_gems()
    if len(hidden_gems) > 0:
        print(hidden_gems.to_string(index=False))
    else:
        print("  未发现遗珠视频")
    
    # 4.2 内容策略建议
    print("\n" + "-"*60)
    print("🎯 功能B2: 内容选择决策树")
    print("-"*60)
    
    # 更新content_advisor的数据（包含质量得分）
    content_advisor = ContentAdvisor(df)
    
    # 打印内容策略报告
    content_advisor.print_report()
    
    # 查看详细推荐
    print("\n【详细内容推荐】")
    recommendations = content_advisor.recommend_next_video()
    
    print("\n推荐内容类型TOP3:")
    for rec in recommendations['推荐类型']:
        print(f"\n  {rec['排名']}. {rec['类型']}")
        print(f"     综合评分: {rec['综合评分']:.2f}")
        print(f"     平均播放: {rec['平均播放']:.0f}")
        print(f"     平均互动率: {rec['平均互动率']:.2f}%")
        print(f"     推荐理由: {rec['理由']}")
    
    # ==================== 5. 生成报告 ====================
    print("\n" + "-"*60)
    print("📈 Step 5: 生成可视化报告")
    print("-"*60)
    
    # 初始化报告生成器
    report_generator = ReportGenerator(df)
    
    # 生成完整报告
    report_generator.generate_full_report(show_plots=False)
    
    print("\n" + "🎉"*40)
    print("  分析完成！所有报告和图表已保存")
    print("🎉"*40 + "\n")


def quick_analysis():
    """
    快速分析模式
    只打印关键信息，不生成完整报告
    适合开发和调试使用
    """
    print("\n⚡ 快速分析模式\n")
    
    # 配置环境
    config.setup_matplotlib()
    config.ensure_dirs()
    
    # 加载数据
    loader = DataLoader(config.ANALYTICS_DATA)
    df = loader.load_data()
    df = loader.preprocess_data()
    
    # 特征工程
    engineer = FeatureEngineer(df)
    df = engineer.add_all_features()
    
    # 快速分析
    report_generator = ReportGenerator(df)
    report_generator.generate_quick_analysis()


if __name__ == "__main__":
    # 运行完整分析
    main()
    
    # 如果只想快速查看结果，可以使用：
    # quick_analysis()
