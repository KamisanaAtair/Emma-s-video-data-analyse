import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import matplotlib.font_manager as fm


class VideoDataAnalyzer:
    """
    视频数据分析器
    用于分析B站视频数据并生成可视化图表
    """
    
    def __init__(self, data_file_path):
        """
        初始化分析器
        
        Args:
            data_file_path (str): 数据文件路径
        """
        self.data_file_path = data_file_path
        self.df = None
        self.setup_chinese_font()
        
    def setup_chinese_font(self):
        """
        设置中文字体支持
        这一步非常重要，因为我们要在图表中显示中文内容（如视频标题、分类等）
        如果不设置，中文会显示为方框或者乱码
        """
        # 尝试几种常见的支持中文的字体
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STSong', 'Arial Unicode MS', 'DejaVu Sans']
        
        # 查找系统中可用的字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 设置可用的中文字体
        for font in chinese_fonts:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                break
        else:
            # 如果找不到预设的中文字体，使用系统默认字体
            print("警告：未找到预设的中文字体，中文可能无法正常显示")
        
        # 解决负号 '-' 显示为方块的问题
        plt.rcParams['axes.unicode_minus'] = False
    
    def load_data(self):
        """加载JSON数据"""
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"成功加载 {len(data)} 条视频数据")
            return data
        except FileNotFoundError:
            print(f"未找到数据文件: {self.data_file_path}")
            return None
        except Exception as e:
            print(f"加载数据时出错: {e}")
            return None
    
    def preprocess_data(self, data):
        """
        预处理数据
        
        Args:
            data (list): 原始数据列表
        """
        self.df = pd.DataFrame(data)
        
        # 转换时间戳为日期
        self.df['created_date'] = pd.to_datetime(self.df['created'], unit='s')
        self.df['year_month'] = self.df['created_date'].dt.to_period('M')
        
        print("数据预处理完成")
    
    def analyze_basic_stats(self):
        """分析基本统计数据"""
        if self.df is None:
            print("请先加载并预处理数据")
            return
        
        print("=== 视频数据基本统计 ===")
        print(f"总计视频数量: {len(self.df)}")
        print(f"发布时间范围: {self.df['created_date'].min()} 至 {self.df['created_date'].max()}")
        print("\n播放量统计:")
        print(self.df['play'].describe())
        print("\n点赞数统计:")
        print(self.df['like'].describe())
        print("\n评论数统计:")
        print(self.df['comment'].describe())
    
    def top_videos_analysis(self):
        """分析热门视频"""
        if self.df is None:
            print("请先加载并预处理数据")
            return
            
        print("\n=== 热门视频分析 ===")
        
        # 播放量前5的视频
        top_play = self.df.nlargest(5, 'play')[['title', 'play', 'like', 'coin']]
        print("\n播放量前5的视频:")
        print(top_play.to_string(index=False))
        
        # 点赞数前5的视频
        top_like = self.df.nlargest(5, 'like')[['title', 'play', 'like', 'coin']]
        print("\n点赞数前5的视频:")
        print(top_like.to_string(index=False))
    
    def create_visualizations(self):
        """
        创建所有可视化图表
        每个图表都是独立的方法，便于维护和扩展
        """
        if self.df is None:
            print("请先加载并预处理数据")
            return
            
        # 创建图表容器
        self.create_play_count_distribution()
        self.create_like_vs_play_scatter()
        self.create_monthly_video_count()
        self.create_interaction_metrics_boxplot()
        
        # 保存并显示图表
        plt.tight_layout()
        plt.savefig('video_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\n图表已保存为 'video_analysis.png'")
    
    def create_play_count_distribution(self):
        """创建播放量分布直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(self.df['play'], bins=30, color='skyblue', edgecolor='black')
        ax.set_title('视频播放量分布')
        ax.set_xlabel('播放量')
        ax.set_ylabel('视频数量')
        plt.close(fig)  # 关闭当前图形，避免显示在最终结果中
        return fig
    
    def create_like_vs_play_scatter(self):
        """创建点赞数vs播放量散点图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(self.df['play'], self.df['like'], alpha=0.6, color='orange')
        ax.set_title('点赞数 vs 播放量')
        ax.set_xlabel('播放量')
        ax.set_ylabel('点赞数')
        plt.close(fig)  # 关闭当前图形，避免显示在最终结果中
        return fig
    
    def create_monthly_video_count(self):
        """创建每月发布视频数量柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        monthly_counts = self.df['year_month'].value_counts().sort_index()
        ax.bar(range(len(monthly_counts)), monthly_counts.values, color='lightgreen')
        ax.set_title('每月发布视频数量')
        ax.set_xlabel('月份')
        ax.set_ylabel('视频数量')
        ax.set_xticks(range(len(monthly_counts)))
        ax.set_xticklabels([str(m) for m in monthly_counts.index], rotation=45)
        plt.close(fig)  # 关闭当前图形，避免显示在最终结果中
        return fig
    
    def create_interaction_metrics_boxplot(self):
        """创建各类互动指标箱线图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        interaction_data = self.df[['play', 'like', 'coin', 'favorite', 'danmaku', 'share', 'comment']]
        ax.boxplot([np.log1p(d) for d in interaction_data.values.T], labels=interaction_data.columns)
        ax.set_title('各类互动指标分布(对数变换)')
        ax.set_ylabel('数值(log)')
        ax.tick_params(axis='x', rotation=45)
        plt.close(fig)  # 关闭当前图形，避免显示在最终结果中
        return fig
    
    def run_complete_analysis(self):
        """运行完整分析流程"""
        # 加载数据
        data = self.load_data()
        if data is None:
            return
        
        # 预处理数据
        self.preprocess_data(data)
        
        # 基本统计分析
        self.analyze_basic_stats()
        
        # 热门视频分析
        self.top_videos_analysis()
        
        # 数据可视化
        self.create_visualizations()
        
        print("\n数据分析完成!")


def main():
    """主函数"""
    analyzer = VideoDataAnalyzer('../JSON_SAVE/analytics_SAVE.json')
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()