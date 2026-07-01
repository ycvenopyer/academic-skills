---
name: paper-analysis
description: 学术论文结构化分析与深度解读。当用户需要全面分析一篇学术论文时使用，包括论文阅读辅助、方法技术分析、实验结果评估、优缺点评价和学术价值判断。支持：自动提取论文结构与统计信息、技术方法检测与分类、贡献点与实验结果抽取、基于分析框架的深度解读。触发词："分析论文"、"论文解读"、"论文分析"、"解读论文"、"深度分析"、"评价论文"。
---

# 学术论文结构化分析

## 分析流程

### 第1步：自动提取论文结构信息

```bash
# 基础分析（基本信息、章节结构、图表统计）
python scripts/analyze_paper.py paper.pdf -o paper_analysis.json

# 标准分析（含方法论检测、贡献点提取）
python scripts/analyze_paper.py paper.pdf --depth standard

# 深度分析
python scripts/analyze_paper.py paper.pdf --depth deep
```

### 第2步：交由 Claude 进行深度解读

将上一步生成的 `paper_analysis.json` 作为输入，结合以下分析框架进行解读。

---

## 🔗 跨技能调用

### 分析前：调用 extract-picture 获取图表信息

分析论文时，提取的图表有助于更全面地评估论文质量：

```bash
# 提取图表供分析参考
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./analysis_figures
python ../extract-picture/scripts/extract_tables.py paper.pdf -o ./analysis_tables

# 查看图表清单
cat ./analysis_figures/_manifest.md
cat ./analysis_tables/_tables_manifest.md
```

在分析报告中引用图表信息：
```
实验分析要点：
- 图3的消融实验清晰地展示了各组件贡献
- 表2的对比结果显示本文方法在3个指标上超越SOTA
```

### 分析后：为 academic-ppt 提供内容支持

分析结果可以直接指导PPT的内容组织：

```bash
# 分析结果中的方法论检测、贡献点和SOTA对比
# 可直接填入PPT的对应幻灯片
python ../academic-ppt/scripts/extract_paper_for_ppt.py paper.pdf -o paper_ppt_data.json

# 编辑 paper_ppt_data.json，将分析报告中的要点填入
# - analysis.contributions → PPT贡献点页
# - analysis.methodology → PPT方法页
# - analysis.structure.sections → PPT目录
```

### 配合 academic-paper-translation

先翻译再分析，确保对论文的深入理解：

```bash
# 1. 先翻译
cd ../academic-paper-translation
python scripts/extract_paper_text.py paper.pdf -o extracted.txt
# → 翻译完成后获得中英对照文本

# 2. 再分析（结合译文更准确）
cd ../paper-analysis
python scripts/analyze_paper.py paper.pdf --depth deep -o analysis.json
```

### 调用 formula2latex 分析公式

识别论文中的公式并评估其复杂度：

```bash
# 提取关键公式（示例：第3页的公式区域）
python ../formula2latex/scripts/formula_ocr.py paper.pdf --pdf --page 3 --region "100,200,500,350" -o formula_eq3.tex

# 在分析报告中讨论公式的创新性和复杂度
```

---

## 🌐 多技能组合工作流

### 完整论文深度分析工作流

```
paper.pdf
    │
    ├── [extract-picture] ─────────────┐
    │   extract_figures.py              │  提取图表用于辅助分析
    │   extract_tables.py               │
    │                                   ▼
    ├── [academic-paper-translation] ──→  翻译辅助理解（可选）
    │   extract_paper_text.py
    │   translate_paper.py              │  用于非英语母语者的深度分析
    │                                   ▼
    ├── [paper-analysis] ──────────────→  核心分析
    │   analyze_paper.py --depth deep
    │   → 结构化JSON + Claude深度解读
    │                                   ▼
    └── [academic-ppt] ────────────────→  分析结果展示
        将分析要点组织为PPT
        → 论文讲解PPT
```

### 快捷方式：完整分析+PPT

```bash
# ========== 论文深度分析 + 汇报PPT 全流程 ==========
PAPER="paper.pdf"
NAME=$(basename "$PAPER" .pdf)

# 1. 提取图表（辅助分析）
python ../extract-picture/scripts/extract_figures.py "$PAPER" -o "${NAME}_figures"
python ../extract-picture/scripts/extract_tables.py "$PAPER" -o "${NAME}_tables"

# 2. 结构化分析
python scripts/analyze_paper.py "$PAPER" --depth deep -o "${NAME}_analysis.json"
echo "✅ 分析完成！查看 ${NAME}_analysis.json"

# 3. 生成PPT结构
python ../academic-ppt/scripts/extract_paper_for_ppt.py "$PAPER" -o "${NAME}_ppt_data.json"

# 4. 生成PPT（含分析要点）
echo "编辑 ${NAME}_ppt_data.json 加入分析要点后执行："
echo "  python ../academic-ppt/scripts/paper_ppt.py ${NAME}_ppt_data.json -o ${NAME}_分析汇报.pptx"
```

---

## 分析框架

参照 [references/analysis_framework.md](references/analysis_framework.md) 中的 **10个分析维度**：

1. 📌 **研究问题与动机** — 解决什么问题？为什么重要？
2. 💡 **方法与创新点** — 核心方法是什么？创新在哪？
3. 🔬 **实验设计** — 数据集、基线、评估指标是否合理？
4. 📊 **实验结果** — 主要发现和统计结果
5. 📐 **理论分析** — 是否有理论保证？
6. 🔄 **可复现性** — 代码和数据是否开放？
7. ✍️ **写作质量** — 结构、图表、公式质量
8. 📚 **相关工作定位** — 相关工作的覆盖和对比
9. ⚠️ **局限性讨论** — 方法的局限性和改进空间
10. 🎯 **综合评估** — 优缺点总结和个人启发

## 分析输出格式

```markdown
# 论文分析报告：论文标题

## 1. 基本信息
- **标题**: ...
- **作者**: ...
- **会议/期刊**: ...
- **年份**: ...
- **关键词**: ...

## 2. 研究问题与动机
（详细分析...）

## 3. 核心方法
（方法描述、架构图说明、关键公式...）

## 4. 实验与结果
（数据集、基线、主要结果、消融实验...）

## 5. 优缺点分析
### 优点
- ...

### 不足/局限性
- ...

## 6. 个人思考与启发
- 对本人研究方向的启示
- 可能的改进方向
- 可借鉴的技术点
```

## 相关技能

| 技能 | 目录 | 在本流程中的角色 |
|------|------|-----------------|
| `extract-picture` | `../extract-picture/` | **前置**: 提取图表供分析参考 |
| `academic-paper-translation` | `../academic-paper-translation/` | **可选前置**: 翻译辅助理解 |
| `formula2latex` | `../formula2latex/` | **可选**: 识别公式供分析 |
| `academic-ppt` | `../academic-ppt/` | **后置**: 将分析结果制作为PPT |

## 依赖安装

```bash
pip install pypdf pdfplumber
```
