# 🚀 快速入门指南

## 第一次使用？按这个步骤来！

### ⏱️ 5分钟快速体验

#### 1. 检查环境

确保你已经安装了Python 3.7或更高版本：

```bash
python --version
```

#### 2. 安装依赖

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

#### 3. 测试系统

运行测试脚本，确保所有模块正常工作：

```bash
python test_system.py
```

如果看到 `🎉 所有测试通过！`，说明系统运行正常。

#### 4. 运行分析

**方式A：完整分析（推荐首次使用）**

```bash
python run_analysis.py
```

这将：
- 分析你的所有视频数据
- 生成详细的文字报告（直接在控制台显示）
- 生成8张可视化图表（保存在 `output/figures/` 目录）

**方式B：快速分析（只看核心结论）**

```bash
python run_analysis.py --quick
```

这将只输出关键结论，不生成图表。

#### 5. 查看结果

**文字报告**：直接在控制台查看

**图表文件**：
- 打开 `output/figures/quality/` 查看质量评分图表
- 打开 `output/figures/content/` 查看内容决策图表

---

## 📖 详细使用指南

### 功能1：视频质量评分

**目的**：评估每个视频的综合质量，找出被埋没的好视频

**如何使用**：

```python
python examples.py
# 选择 [2] 质量评分分析
```

**你会得到**：
- 每个视频的0-100分质量评分
- 质量分布情况
- TOP质量视频列表
- "遗珠"视频列表（高质量但低播放）
- 具体改进建议

**关键图表**：
- `B1-1_quality_score_distribution.png` - 质量分布
- `B1-2_quality_vs_play_scatter.png` - 发现遗珠视频

---

### 功能2：内容选择决策

**目的**：基于数据推荐下一个视频做什么内容

**如何使用**：

```python
python examples.py
# 选择 [3] 内容决策分析
```

**你会得到**：
- 各类型内容的表现排行
- 最佳视频时长建议
- 标题特征的影响分析
- TOP3推荐内容方向

**关键图表**：
- `B2-1_content_type_performance.png` - 内容类型对比
- `B2-4_roi_ranking.png` - ROI排行榜

---

## 🎯 根据你的目标选择功能

### 目标：快速涨粉

1. 运行完整分析：`python run_analysis.py`
2. 重点看：
   - **内容推荐**：做什么类型的视频
   - **爆款视频特征**：学习成功经验
   - **ROI排行**：性价比最高的内容

### 目标：提升视频质量

1. 运行质量评分：`python examples.py` → 选择[2]
2. 重点看：
   - **质量分布**：你的视频处于什么水平
   - **低质量视频**：哪些需要改进
   - **改进建议**：具体怎么改

### 目标：找到定位

1. 运行内容决策：`python examples.py` → 选择[3]
2. 重点看：
   - **内容类型表现**：你擅长什么
   - **内容空白区**：未开发的机会
   - **最佳组合**：内容类型 × 视频时长

---

## 💡 常见场景

### 场景1：新视频发布前

**问题**：不知道做什么内容

**操作**：
```bash
python run_analysis.py
```

查看【内容推荐】部分，选择推荐的TOP3内容类型之一。

---

### 场景2：视频数据更新后

**问题**：爬取了新的数据，想看最新分析

**操作**：
1. 用爬虫更新 `JSON_SAVE/analytics_SAVE.json`
2. 重新运行：`python run_analysis.py`

---

### 场景3：对比不同时期

**问题**：想看账号是否在进步

**操作**：
```bash
python examples.py
# 选择 [6] 时间段对比分析
```

---

### 场景4：只想看图表

**问题**：已经看过文字报告，只想更新图表

**操作**：
```bash
python examples.py
# 选择 [4] 生成可视化图表
```

---

## ⚙️ 自定义配置

### 修改爆款视频的定义

编辑 `config.py`：

```python
VIRAL_VIDEO_THRESHOLD = {
    'play_multiplier': 2.0,      # 改为1.5：降低标准
    'min_play_count': 1000,      # 改为500：降低播放量要求
    'min_engagement_rate': 5.0   # 改为3.0：降低互动率要求
}
```

### 修改质量评分权重

编辑 `config.py`：

```python
QUALITY_SCORE_WEIGHTS = {
    'play_score': 0.30,      # 播放量权重
    'engagement_score': 0.40,  # 互动率权重（最重要）
    'spread_score': 0.20,    # 传播力权重
    'duration_score': 0.10   # 持久性权重
}
```

### 添加新的内容类型

编辑 `config.py`：

```python
CONTENT_TYPE_KEYWORDS = {
    '游戏切片': ['切片', '合集', '集锦'],
    '新类型': ['关键词1', '关键词2'],  # 添加这一行
    # ...
}
```

---

## 🐛 遇到问题？

### 问题1：ModuleNotFoundError

**解决**：安装缺失的模块
```bash
pip install 模块名
```

### 问题2：中文显示乱码

**解决**：修改 `config.py` 中的 `CHINESE_FONTS` 列表，添加你系统中的中文字体。

查看系统字体：
```python
import matplotlib.font_manager as fm
fonts = [f.name for f in fm.fontManager.ttflist if 'SimHei' in f.name or 'Microsoft' in f.name]
print(fonts)
```

### 问题3：图表保存失败

**解决**：确保 `output/figures/` 目录有写入权限。

### 问题4：数据文件找不到

**解决**：检查 `JSON_SAVE/analytics_SAVE.json` 是否存在。

---

## 📚 进阶使用

### 使用Python代码调用

```python
from bilibili_analyzer.core import DataLoader, FeatureEngineer, MetricsCalculator
from bilibili_analyzer.analyzers import QualityScorer

# 加载数据
loader = DataLoader('JSON_SAVE/analytics_SAVE.json')
df = loader.load_and_process()

# 特征工程
engineer = FeatureEngineer(df)
df = engineer.engineer_all_features()

# 计算质量分
calculator = MetricsCalculator(df)
df = calculator.calculate_quality_score()

# 生成报告
scorer = QualityScorer(df)
report = scorer.generate_quality_report()

# 获取TOP5质量视频
top5 = report['top_quality_videos'].head(5)
print(top5[['title', 'quality_score', 'play']])
```

### 导出数据到Excel

```python
from bilibili_analyzer.analyzers import QualityScorer

# ... 前面的步骤 ...

scorer = QualityScorer(df)
scorer.export_quality_scores('output/my_quality_scores.xlsx')
```

---

## 🎓 学习路线

### 第1周：熟悉基础功能
- [ ] 运行完整分析，理解所有报告
- [ ] 查看所有图表，理解每张图的含义
- [ ] 根据建议调整1-2个视频的内容方向

### 第2周：深入使用
- [ ] 尝试自定义配置
- [ ] 使用examples.py探索各个功能
- [ ] 对比不同时间段的数据

### 第3周：进阶应用
- [ ] 学习Python代码调用方式
- [ ] 进行自定义分析
- [ ] 结合实际运营效果验证建议

---

## 📞 获取帮助

- 查看 `README.md` 了解详细功能
- 运行 `python examples.py` 查看使用示例
- 阅读代码注释了解实现原理

---

**祝你玩得开心！** 🎉
