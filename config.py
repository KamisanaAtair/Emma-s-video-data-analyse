"""
全局配置文件
用于统一管理项目的所有配置参数，便于维护和调整
"""

import os
from pathlib import Path

# ==================== 路径配置 ====================
# 项目根目录
ROOT_DIR = Path(__file__).parent

# 数据文件路径
DATA_DIR = ROOT_DIR / "JSON_SAVE"
ANALYTICS_DATA_FILE = DATA_DIR / "analytics_SAVE.json"
BASIC_DATA_FILE = DATA_DIR / "basic_SAVE.json"
USER_VIDEOS_FILE = DATA_DIR / "user_videos_SAVE.json"

# 输出目录
OUTPUT_DIR = ROOT_DIR / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"

# 确保输出目录存在
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== 可视化配置 ====================
# 图表样式
PLOT_STYLE = 'seaborn-v0_8-darkgrid'  # matplotlib样式
FIGURE_DPI = 300  # 图片分辨率
FIGURE_FORMAT = 'png'  # 图片格式

# 中文字体配置（按优先级尝试）
CHINESE_FONTS = ['SimHei', 'Microsoft YaHei', 'STSong', 'Arial Unicode MS', 'DejaVu Sans']

# 颜色配置
COLOR_PALETTE = {
    'primary': '#1f77b4',      # 主色调 - 蓝色
    'secondary': '#ff7f0e',    # 次要色 - 橙色
    'success': '#2ca02c',      # 成功/积极 - 绿色
    'warning': '#d62728',      # 警告/消极 - 红色
    'info': '#9467bd',         # 信息 - 紫色
    'neutral': '#7f7f7f'       # 中性 - 灰色
}

# 图表尺寸配置
FIGURE_SIZES = {
    'small': (8, 6),
    'medium': (10, 8),
    'large': (12, 10),
    'wide': (14, 6)
}


# ==================== 数据分析配置 ====================
# 视频时长分段（秒）
LENGTH_BINS = [0, 30, 60, 180, 300, 600, float('inf')]
LENGTH_LABELS = ['<30秒', '30秒-1分钟', '1-3分钟', '3-5分钟', '5-10分钟', '>10分钟']

# 播放量分段（用于分类分析）
PLAY_BINS = [0, 100, 300, 500, 1000, 3000, float('inf')]
PLAY_LABELS = ['<100', '100-300', '300-500', '500-1000', '1000-3000', '>3000']

# 爆款视频定义阈值
VIRAL_VIDEO_THRESHOLD = {
    'play_multiplier': 2.0,      # 播放量 > 平均值的N倍
    'min_play_count': 1000,      # 或播放量 > N
    'min_engagement_rate': 5.0   # 且互动率 > N%
}

# 视频质量评分权重
QUALITY_SCORE_WEIGHTS = {
    'play_score': 0.30,      # 播放吸引力权重
    'engagement_score': 0.40,  # 内容质量权重
    'spread_score': 0.20,    # 传播力权重
    'duration_score': 0.10   # 持久性权重（目前没有历史数据，可设为0）
}

# 互动率计算权重
ENGAGEMENT_WEIGHTS = {
    'like_rate': 0.35,
    'coin_rate': 0.30,
    'favorite_rate': 0.25,
    'comment_rate': 0.10
}


# ==================== B站分区配置 ====================
# B站视频分区映射
BILIBILI_CATEGORIES = {
    1: "动画",
    3: "音乐",
    4: "游戏",
    17: "单机游戏",
    27: "综合",
    31: "翻唱",
    171: "电子竞技",
    210: "动物圈"
}

# 内容类型分类（自定义规则）
CONTENT_TYPE_KEYWORDS = {
    '游戏切片': ['切片', '合集', '集锦'],
    '游戏实况': ['打工', '找岛民'],
    '恐怖游戏': ['恐鬼', '逃生'],
    '模型展示': ['模型展示', 'Live2d', 'Live2D'],
    '唱歌': ['翻唱', 'アイドル', '恶者', 'Chu'],
    '自我介绍': ['自我介绍', '见习恶魔'],
    '助眠': ['助眠'],
    '展示': ['小岛展示', '小屋展示', 'Room Tour']
}


# ==================== 报告生成配置 ====================
# 报告标题配置
REPORT_TITLE = "B站UP主数据分析报告"
REPORT_SUBTITLE = "基于视频数据的深度分析与决策建议"

# 报告输出格式
REPORT_FORMATS = ['html', 'markdown']  # 支持的报告格式


# ==================== 日志配置 ====================
# 日志级别
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
