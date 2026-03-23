"""
测试脚本：验证所有模块是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
from bilibili_analyzer.analyzers import QualityScorer, ContentAdvisor
from bilibili_analyzer.visualizers import BaseVisualizer, ReportGenerator


def test_data_loader():
    """测试数据加载器"""
    print("\n【测试1/7】数据加载器...")
    try:
        loader = DataLoader(config.ANALYTICS_DATA_FILE)
        df = loader.load_and_process()
        
        if df is not None and len(df) > 0:
            print(f"✓ 数据加载成功：{len(df)} 条记录")
            return df
        else:
            print("✗ 数据加载失败")
            return None
    except Exception as e:
        print(f"✗ 数据加载器错误：{e}")
        return None


def test_feature_engineer(df):
    """测试特征工程"""
    print("\n【测试2/7】特征工程...")
    try:
        engineer = FeatureEngineer(df)
        df_engineered = engineer.engineer_all_features()
        
        # 检查是否生成了新特征
        required_features = ['engagement_rate', 'content_type', 'is_viral', 'length_category']
        missing_features = [f for f in required_features if f not in df_engineered.columns]
        
        if not missing_features:
            print(f"✓ 特征工程成功：新增特征 {len(df_engineered.columns) - len(df.columns)} 个")
            return df_engineered
        else:
            print(f"✗ 缺少特征：{missing_features}")
            return None
    except Exception as e:
        print(f"✗ 特征工程错误：{e}")
        return None


def test_metrics_calculator(df):
    """测试指标计算器"""
    print("\n【测试3/7】指标计算器...")
    try:
        calculator = MetricsCalculator(df)
        df_with_scores = calculator.calculate_quality_score()
        
        # 检查质量分是否计算
        if 'quality_score' in df_with_scores.columns:
            avg_score = df_with_scores['quality_score'].mean()
            print(f"✓ 指标计算成功：平均质量分 {avg_score:.1f}")
            return df_with_scores
        else:
            print("✗ 质量分计算失败")
            return None
    except Exception as e:
        print(f"✗ 指标计算器错误：{e}")
        return None


def test_quality_scorer(df):
    """测试质量评分系统"""
    print("\n【测试4/7】质量评分系统...")
    try:
        scorer = QualityScorer(df)
        report = scorer.generate_quality_report()
        
        # 检查报告是否生成
        required_keys = ['summary', 'top_quality_videos', 'improvement_recommendations']
        missing_keys = [k for k in required_keys if k not in report]
        
        if not missing_keys:
            print(f"✓ 质量报告生成成功")
            print(f"  - 平均质量分：{report['summary']['avg_quality_score']:.1f}")
            print(f"  - 高质量视频：{report['summary']['high_quality_count']} 个")
            return True
        else:
            print(f"✗ 报告缺少关键信息：{missing_keys}")
            return False
    except Exception as e:
        print(f"✗ 质量评分系统错误：{e}")
        return False


def test_content_advisor(df):
    """测试内容决策系统"""
    print("\n【测试5/7】内容决策系统...")
    try:
        advisor = ContentAdvisor(df)
        analysis = advisor.analyze_content_performance()
        
        # 检查分析是否完成
        required_keys = ['by_content_type', 'by_length', 'best_combinations']
        missing_keys = [k for k in required_keys if k not in analysis]
        
        if not missing_keys:
            recommendations = advisor.generate_recommendations(top_n=3)
            print(f"✓ 内容决策分析成功")
            print(f"  - 内容类型数：{len(analysis['by_content_type'])}")
            print(f"  - 推荐建议数：{len(recommendations)}")
            return True
        else:
            print(f"✗ 分析缺少关键信息：{missing_keys}")
            return False
    except Exception as e:
        print(f"✗ 内容决策系统错误：{e}")
        return False


def test_base_visualizer():
    """测试基础可视化"""
    print("\n【测试6/7】基础可视化...")
    try:
        visualizer = BaseVisualizer()
        print("✓ 可视化器初始化成功")
        return True
    except Exception as e:
        print(f"✗ 可视化器错误：{e}")
        return False


def test_report_generator(df):
    """测试报告生成器"""
    print("\n【测试7/7】报告生成器...")
    try:
        generator = ReportGenerator(df)
        
        # 测试单个图表生成
        import matplotlib.pyplot as plt
        fig = generator.plot_quality_score_distribution()
        plt.close(fig)
        
        print("✓ 报告生成器测试成功")
        print("  （注：完整图表生成较慢，这里只测试了一个图表）")
        return True
    except Exception as e:
        print(f"✗ 报告生成器错误：{e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 开始测试所有模块".center(80))
    print("="*80)
    
    # 测试计数
    total_tests = 7
    passed_tests = 0
    
    # 1. 数据加载器
    df = test_data_loader()
    if df is not None:
        passed_tests += 1
    else:
        print("\n✗ 数据加载失败，无法继续测试")
        return
    
    # 2. 特征工程
    df = test_feature_engineer(df)
    if df is not None:
        passed_tests += 1
    else:
        print("\n✗ 特征工程失败，无法继续测试")
        return
    
    # 3. 指标计算器
    df = test_metrics_calculator(df)
    if df is not None:
        passed_tests += 1
    else:
        print("\n✗ 指标计算失败，无法继续测试")
        return
    
    # 4. 质量评分系统
    if test_quality_scorer(df):
        passed_tests += 1
    
    # 5. 内容决策系统
    if test_content_advisor(df):
        passed_tests += 1
    
    # 6. 基础可视化
    if test_base_visualizer():
        passed_tests += 1
    
    # 7. 报告生成器
    if test_report_generator(df):
        passed_tests += 1
    
    # 测试结果汇总
    print("\n" + "="*80)
    print("📊 测试结果汇总".center(80))
    print("="*80)
    print(f"\n  总测试数：{total_tests}")
    print(f"  通过测试：{passed_tests}")
    print(f"  失败测试：{total_tests - passed_tests}")
    print(f"  通过率：{passed_tests / total_tests * 100:.1f}%\n")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_tests()
