"""
全局配置文件
包含所有分析参数、阈值、图表样式等配置
"""

import matplotlib.pyplot as plt
from pathlib import Path

class Config:
    """全局配置类"""
    
    # ==================== 路径配置 ====================
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # 数据文件路径
    DATA_DIR = PROJECT_ROOT / "JSON_SAVE"
    ANALYTICS_DATA = DATA_DIR / "analytics_SAVE.json"
    BASIC_DATA = DATA_DIR / "basic_SAVE.json"
    USER_VIDEOS_DATA = DATA_DIR / "user_videos_SAVE.json"
    
    # 输出目录
    OUTPUT_DIR = PROJECT_ROOT / "analysis_output"
    CHARTS_DIR = OUTPUT_DIR / "charts"
    REPORTS_DIR = OUTPUT_DIR / "reports"
    
    # ==================== 分析参数配置 ====================
    
    # 视频质量评分权重配置
    QUALITY_WEIGHTS = {
        'play_score': 0.30,      # 播放量得分权重
        'interaction_score': 0.40,  # 互动率得分权重
        'spread_score': 0.20,    # 传播力得分权重
        'durability_score': 0.10  # 持久性得分权重（暂时无法计算，预留）
    }
    
    # 爆款视频定义阈值
    VIRAL_VIDEO_THRESHOLD = {
        'play_multiplier': 2.0,  # 播放量超过平均值的倍数
        'min_play_count': 1000,  # 最低播放量
    }
    
    # 视频时长分段（秒）
    VIDEO_LENGTH_BINS = [0, 30, 60, 180, 300, 600, float('inf')]
    VIDEO_LENGTH_LABELS = ['<30秒', '30秒-1分钟', '1-3分钟', '3-5分钟', '5-10分钟', '>10分钟']
    
    # 互动率阈值（用于分类视频质量）
    INTERACTION_RATE_THRESHOLD = {
        'excellent': 8.0,   # 优秀：>8%
        'good': 5.0,        # 良好：5-8%
        'normal': 3.0,      # 一般：3-5%
        'poor': 0           # 较差：<3%
    }
    
    # ==================== 可视化配置 ====================
    
    # 中文字体配置（按优先级）
    CHINESE_FONTS = ['SimHei', 'Microsoft YaHei', 'STSong', 'Arial Unicode MS', 'DejaVu Sans']
    
    # 图表默认尺寸
    DEFAULT_FIGURE_SIZE = (12, 8)
    SMALL_FIGURE_SIZE = (10, 6)
    LARGE_FIGURE_SIZE = (14, 10)
    
    # 图表样式
    CHART_STYLE = 'seaborn-v0_8-darkgrid'
    
    # 颜色配置
    COLOR_PALETTE = {
        'primary': '#5470C6',      # 主色调
        'success': '#91CC75',      # 成功/良好
        'warning': '#FAC858',      # 警告/一般
        'danger': '#EE6666',       # 危险/较差
        'info': '#73C0DE',         # 信息
        'viral': '#FC8452',        # 爆款标记
        'normal': '#9A60B4'        # 普通
    }
    
    # 图表配置
    CHART_CONFIG = {
        'dpi': 300,
        'bbox_inches': 'tight',
        'facecolor': 'white',
        'edgecolor': 'none'
    }
    
    # ==================== 分析文本配置 ====================
    
    # 分区映射（B站分区ID对应的中文名称）
    TYPEID_MAPPING = {
        17: '单机游戏',
        27: '综合',
        31: '翻唱',
        171: '电子竞技',
        210: '手机游戏',
        # 可以根据需要添加更多分区
    }
    
    # 质量评级文本
    QUALITY_RATING = {
        'S': '优秀（S级）',
        'A': '良好（A级）',
        'B': '一般（B级）',
        'C': '较差（C级）'
    }
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有必要的目录存在"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.CHARTS_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def setup_matplotlib(cls):
        """配置matplotlib的全局设置"""
        import matplotlib.font_manager as fm
        
        # 查找可用的中文字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in cls.CHINESE_FONTS:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                print(f"✓ 已设置中文字体: {font}")
                break
        else:
            print("⚠ 警告：未找到预设的中文字体，中文可能无法正常显示")
        
        # 解决负号显示问题
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置默认样式
        try:
            plt.style.use(cls.CHART_STYLE)
        except:
            print(f"⚠ 警告：样式 {cls.CHART_STYLE} 不可用，使用默认样式")
        
        # 设置默认图表大小
        plt.rcParams['figure.figsize'] = cls.DEFAULT_FIGURE_SIZE
        
        print("✓ Matplotlib配置完成")


# 创建全局配置实例
config = Config()
