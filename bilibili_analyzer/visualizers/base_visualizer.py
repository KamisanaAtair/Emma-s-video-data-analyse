"""
基础可视化模块
提供所有图表绘制的基础功能
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))
import config


class BaseVisualizer:
    """
    基础可视化类
    
    功能：
    1. 配置图表样式和中文字体
    2. 提供各类常用图表的绘制方法
    3. 统一的图表保存功能
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化可视化器
        
        Args:
            output_dir: 图表输出目录
        """
        self.output_dir = output_dir or config.FIGURES_DIR
        self.setup_style()
        
    def setup_style(self):
        """
        设置matplotlib样式和中文字体
        """
        # 设置seaborn样式
        sns.set_style("whitegrid")
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 配置中文字体
        self._setup_chinese_font()
        
        # 解决负号显示问题
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置默认图表大小
        plt.rcParams['figure.figsize'] = config.FIGURE_SIZES['medium']
        
        # 设置DPI
        plt.rcParams['figure.dpi'] = config.FIGURE_DPI
        
        print("✓ 图表样式配置完成")
    
    def _setup_chinese_font(self):
        """
        配置中文字体
        """
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in config.CHINESE_FONTS:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                print(f"✓ 使用中文字体：{font}")
                return
        
        print("⚠ 警告：未找到合适的中文字体，中文可能无法正常显示")
    
    def save_figure(self, fig: plt.Figure, filename: str, subfolder: str = ""):
        """
        保存图表到文件
        
        Args:
            fig: matplotlib图表对象
            filename: 文件名
            subfolder: 子文件夹名称（可选）
        """
        # 创建子文件夹（如果指定）
        if subfolder:
            save_dir = self.output_dir / subfolder
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.output_dir
        
        # 完整文件路径
        filepath = save_dir / f"{filename}.{config.FIGURE_FORMAT}"
        
        # 保存图表
        fig.savefig(filepath, dpi=config.FIGURE_DPI, bbox_inches='tight')
        print(f"✓ 图表已保存：{filepath}")
        
        return filepath
    
    # ==================== 基础图表绘制方法 ====================
    
    def plot_bar(self, data: pd.Series, title: str, xlabel: str, ylabel: str,
                 figsize: Tuple[int, int] = (10, 6), color: str = None) -> plt.Figure:
        """
        绘制柱状图
        
        Args:
            data: 数据（Series类型）
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            figsize: 图表大小
            color: 柱子颜色
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        color = color or config.COLOR_PALETTE['primary']
        data.plot(kind='bar', ax=ax, color=color, edgecolor='black', alpha=0.8)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_scatter(self, x: pd.Series, y: pd.Series, title: str, 
                    xlabel: str, ylabel: str, labels: Optional[pd.Series] = None,
                    figsize: Tuple[int, int] = (10, 8), color: str = None) -> plt.Figure:
        """
        绘制散点图
        
        Args:
            x: X轴数据
            y: Y轴数据
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            labels: 数据点标签（可选）
            figsize: 图表大小
            color: 点颜色
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        color = color or config.COLOR_PALETTE['primary']
        ax.scatter(x, y, alpha=0.6, s=100, color=color, edgecolors='black', linewidth=0.5)
        
        # 如果提供了标签，添加标注（只标注部分点，避免重叠）
        if labels is not None:
            # 只标注TOP5的点
            top_indices = y.nlargest(5).index
            for idx in top_indices:
                if idx in labels.index:
                    ax.annotate(labels[idx][:20], (x[idx], y[idx]), 
                              fontsize=8, alpha=0.7,
                              xytext=(5, 5), textcoords='offset points')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_line(self, data: pd.DataFrame, title: str, xlabel: str, ylabel: str,
                  figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """
        绘制折线图
        
        Args:
            data: 数据（DataFrame类型，可包含多列）
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        data.plot(ax=ax, linewidth=2, marker='o', markersize=5)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(loc='best')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_pie(self, data: pd.Series, title: str, 
                 figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """
        绘制饼图
        
        Args:
            data: 数据（Series类型）
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = sns.color_palette("Set3", len(data))
        wedges, texts, autotexts = ax.pie(
            data.values, 
            labels=data.index, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )
        
        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def plot_heatmap(self, data: pd.DataFrame, title: str,
                    figsize: Tuple[int, int] = (10, 8), cmap: str = "RdYlGn") -> plt.Figure:
        """
        绘制热力图
        
        Args:
            data: 数据（DataFrame类型）
            title: 图表标题
            figsize: 图表大小
            cmap: 颜色映射
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(data, annot=True, fmt='.2f', cmap=cmap, 
                   center=0, square=True, linewidths=0.5,
                   cbar_kws={"shrink": 0.8}, ax=ax)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def plot_boxplot(self, data: pd.DataFrame, title: str, xlabel: str, ylabel: str,
                    figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """
        绘制箱线图
        
        Args:
            data: 数据（DataFrame类型）
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        data.plot(kind='box', ax=ax, patch_artist=True,
                 boxprops=dict(facecolor=config.COLOR_PALETTE['primary'], alpha=0.7))
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_grouped_bar(self, data: pd.DataFrame, title: str, xlabel: str, ylabel: str,
                        figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """
        绘制分组柱状图
        
        Args:
            data: 数据（DataFrame类型，行为分类，列为分组）
            title: 图表标题
            xlabel: X轴标签
            ylabel: Y轴标签
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        data.plot(kind='bar', ax=ax, width=0.8, edgecolor='black', alpha=0.8)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='best')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 测试基础可视化功能
    visualizer = BaseVisualizer()
    
    # 示例数据
    data = pd.Series([100, 200, 150, 300, 250], index=['A', 'B', 'C', 'D', 'E'])
    
    # 绘制柱状图
    fig = visualizer.plot_bar(data, '测试柱状图', 'X轴', 'Y轴')
    visualizer.save_figure(fig, 'test_bar')
    plt.close()
    
    print("✓ 测试完成")
