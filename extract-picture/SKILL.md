---
name: extract-picture
description: 论文PDF图片和表格提取工具。当用户需要从学术论文PDF中提取图片（Figure）、表格（Table）及其标题时使用。支持：PDF内嵌图片提取、表格数据提取为CSV/Excel/Markdown、图表标题自动检测与关联。触发词："提取图片"、"提取表格"、"论文图片"、"论文图表"、"提取图表"。
---

# 论文PDF图片与表格提取

## 提取流程

### 第1步：提取图片

```bash
# 基本用法（提取所有图片到 ./<论文名>_figures/）
python scripts/extract_figures.py paper.pdf

# 指定输出目录和格式
python scripts/extract_figures.py paper.pdf -o ./figures --format png

# 过滤小图标（只提取 ≥300x300 的图片）
python scripts/extract_figures.py paper.pdf --min-size 300x300

# 使用 pdfimages 引擎（更全面但需安装 poppler）
python scripts/extract_figures.py paper.pdf --engine pdfimages

# 提取同时指定图片格式
python scripts/extract_figures.py paper.pdf --format jpg
```

### 第2步：提取表格

```bash
# 基本用法（导出为 CSV + Excel + Markdown）
python scripts/extract_tables.py paper.pdf

# 指定格式
python scripts/extract_tables.py paper.pdf -f csv,md

# 使用 camelot 引擎（适合带边框的复杂表格）
python scripts/extract_tables.py paper.pdf --engine camelot
```

---

## 🔗 作为数据源供其他技能调用

`extract-picture` 的核心角色是**数据提供者**——提取的图表数据和清单被其他技能消费。

### 被 academic-paper-translation 调用

翻译前提取图表，让翻译过程能直接引用图表的实际内容：

```bash
# 在 academic-paper-translation 流程中调用本技能
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./paper_figures
python ../extract-picture/scripts/extract_tables.py paper.pdf -o ./paper_tables

# 查看图表清单，获取 Figure/Table 的编号和标题
cat ./paper_figures/_manifest.md
cat ./paper_tables/_tables_manifest.md
```

提取的图表在翻译中用于：
- 确认 `Figure N` → `图N` 的编号对应关系
- 查看图片内容以确保翻译准确（如架构图中的组件名称）
- 表格数据可直接转为中英双语Markdown表格

### 被 academic-ppt 调用

制作PPT时，提取的图表直接插入幻灯片：

```bash
# 在 academic-ppt 流程中调用本技能
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./ppt_figures
python ../extract-picture/scripts/extract_tables.py paper.pdf -o ./ppt_tables
```

PPT中的使用方式：
- 架构图 → 插入方法页
- 结果图表 → 插入实验页
- 表格数据 → 转为PPT表格

### 被 formula2latex 调用

从PDF提取的图片中筛选出公式图，批量识别LaTeX：

```bash
# 在 formula2latex 流程中调用本技能
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./all_figures

# 筛选出公式图片后批量识别
python ../formula2latex/scripts/formula_ocr.py --folder ./all_figures/
```

### 被 paper-analysis 调用

分析论文时，提取的图表用于辅助理解和评估：

```bash
# 提取图表供分析参考
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./analysis_figures
```

---

## 输出结构

### 图片提取输出

```
<论文名>_figures/
├── _manifest.md          # 图片提取清单（含页面、尺寸、格式信息、检测到的标题）
├── page001_img01.png     # 第1页第1张图
├── page001_img02.png     # 第1页第2张图
└── ...
```

`_manifest.md` 中包含检测到的图表标题（Figure/Table Caption），便于人工匹配图片和标题。

### 表格提取输出

```
<论文名>_tables/
├── _tables_manifest.md   # 表格提取清单
├── table_01_Table1.csv   # 表1 - CSV格式
├── table_01_Table1.xlsx  # 表1 - Excel格式
├── table_01_Table1.md    # 表1 - Markdown格式
└── table_02_...
```

## 图表标题关联

提取的图片文件名包含页面信息（`page001_img01.png`），检测到的图表标题也包含页码，据此进行关联：

```
_manifest.md 内容示例：
| 序号 | 页面 | 文件名 | 宽度 | 高度 | 格式 |
|------|------|--------|------|------|------|
| 1    | 1    | page001_img01.png | 1200 | 800 | png |

检测到的图表标题：
- 🖼️ **Figure 1** (第1页): Overview of the proposed architecture
- 📊 **Table 1** (第2页): Comparison with state-of-the-art methods
```

## 提取后的人工校对要点

1. **图片筛选** — PDF中可能包含图标、logo等小图，人工筛选出论文核心图表
2. **图题对应** — 确认提取的图片与检测到的标题一一对应
3. **表格验证** — 检查提取的表格数据是否完整，有无合并单元格错位
4. **清晰度检查** — 如果图片模糊，尝试使用 `--engine pdfimages` 重新提取
5. **路径记录** — 记录提取目录的路径，供下游技能引用

## 相关技能

| 技能 | 目录 | 在本流程中的角色 |
|------|------|-----------------|
| `academic-paper-translation` | `../academic-paper-translation/` | **消费方**: 翻译时引用图表内容 |
| `academic-ppt` | `../academic-ppt/` | **消费方**: PPT中插入图表 |
| `formula2latex` | `../formula2latex/` | **消费方**: 从图片中筛选公式识别 |
| `paper-analysis` | `../paper-analysis/` | **消费方**: 分析时参考图表 |

## 依赖安装

```bash
pip install pypdf pdfplumber PyMuPDF pandas openpyxl

# 如需 OCR（扫描版PDF中的表格）
pip install pdf2image pytesseract

# 如需 camelot 引擎（更好的表格提取）
pip install camelot-py[cv]
```
