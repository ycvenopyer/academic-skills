---
name: academic-ppt
description: 学术论文组会汇报PPT制作。当用户需要将学术论文制作成PPT用于组会汇报、学术报告或论文答辩时使用。支持：论文内容自动提取与分析、结构化PPT生成（标题/背景/方法/实验/总结）、标准学术配色与排版、中英双语PPT、自动插入论文图表。触发词："做PPT"、"组会PPT"、"汇报PPT"、"论文PPT"、"学术PPT"、"生成PPT"。
---

# 学术论文组会汇报PPT制作

## 核心工作流

### 第1步：提取论文并生成PPT结构

```bash
# 从PDF提取论文信息，生成幻灯片结构JSON
python scripts/extract_paper_for_ppt.py paper.pdf -o paper_ppt_data.json
```

### 第2步：直接生成PPTX（快速版）

```bash
# 基本用法
python scripts/paper_ppt.py paper_ppt_data.json -o 组会汇报.pptx

# 带图表插入（先调用 extract-picture 提取图表）
python scripts/paper_ppt.py paper_ppt_data.json --figures-dir ./paper_figures -o 组会汇报.pptx

# 中英双语PPT（需在JSON中设置 bilingual 字段）
python scripts/paper_ppt.py paper_ppt_data.json -o 中英双语汇报.pptx
```

### 第3步：精美版 - 使用 html2pptx（推荐）

如需更精美的PPT（自定义配色、图表、布局），使用 html2pptx 工作流：

```bash
# 1. 查看 pptx 技能的 html2pptx 指南（先完整阅读）
#    参考: 系统中ppt技能里的 html2pptx.md

# 2. 根据 paper_ppt_data.json 中的幻灯片结构，为每页创建HTML文件
#    例如: slide_01_title.html, slide_02_outline.html ...

# 3. 使用 html2pptx 库转换为 PPTX
```

详细流程参考 [pptx 技能的 html2pptx 指南]（位于系统中 pptx 技能的 html2pptx.md 文件，需要先完整阅读）。

---

## 🔗 跨技能调用 — 调用 extract-picture 插入图表

### 在PPT中插入论文图片

```bash
# 1. 先用 extract-picture 提取论文中的图片
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./paper_figures

# 2. 生成PPT时自动插入图表
python scripts/paper_ppt.py paper_ppt_data.json --figures-dir ./paper_figures -o 含图PPT.pptx
```

`paper_ppt.py` 会根据幻灯片标题自动匹配图片：
- "方法 (Method)" 页 → 自动查找架构图
- "实验 (Experiment)" 页 → 自动查找结果图
- 匹配逻辑：读取 `_manifest.md` 中的Figure标题，与当前页标题做关键词匹配

### 在PPT中插入论文表格

```bash
# 先用 extract-picture 提取表格
python ../extract-picture/scripts/extract_tables.py paper.pdf -o ./paper_tables

# 提取的 Markdown 表格可直接复制到JSON的 content 字段中
cat ./paper_tables/table_01_*.md
```

编辑 `paper_ppt_data.json`，在相应幻灯片的 `content` 中嵌入表格数据：

```json
{
  "slides": [
    {
      "type": "content",
      "title": "实验结果 (Experimental Results)",
      "content": "表1：与基线方法对比\n| 方法 | 准确率 | F1分数 |\n|------|--------|--------|\n| 基线A | 85.2 | 83.1 |\n| 基线B | 88.7 | 86.5 |\n| 本文方法 | 91.5 | 89.7 |"
    }
  ]
}
```

---

## 🔗 跨技能调用 — 与 academic-paper-translation 配合制作双语PPT

利用翻译结果制作**中英双语汇报PPT**，每页同时显示原文和译文。

### 工作流

```bash
# 1. 先用 academic-paper-translation 完成翻译
cd ../academic-paper-translation
# 注意: paper.pdf 路径根据实际情况调整，也可以用绝对路径
python scripts/extract_paper_text.py ../academic-ppt/paper.pdf -o extracted.txt
python scripts/translate_paper.py extracted.txt -o translation.md
# → 编辑 translation.md 完成逐段翻译
cd ../academic-ppt

# 2. 提取PPT结构并嵌入翻译内容
python scripts/extract_paper_for_ppt.py paper.pdf -o paper_ppt_data.json

# 3. 编辑 paper_ppt_data.json，为每页添加 bilingual 字段
# 4. 生成双语PPT
python scripts/paper_ppt.py paper_ppt_data.json -o 中英双语汇报.pptx
```

### 配置双语幻灯片

编辑 `paper_ppt_data.json`，为每页添加 `bilingual`、`original` 和 `translation` 字段：

```json
{
  "slides": [
    {
      "type": "content",
      "title": "Introduction (引言)",
      "bilingual": true,
      "original": "Deep learning has achieved great success in various fields...",
      "translation": "深度学习在各个领域取得了巨大成功..."
    }
  ]
}
```

### 生成双语PPT

```bash
python scripts/paper_ppt.py paper_ppt_data.json -o 中英双语汇报.pptx
```

生成的PPT每页布局为：
- 左侧栏：英文原文（灰色小字）
- 右侧栏：中文译文（深色大字）

---

## 🌐 多技能组合工作流

### 完整学术汇报PPT制作流程

```
paper.pdf
    │
    ├── [extract-picture] ─────────────┐
    │   extract_figures.py              │  提取图表用于PPT插图
    │   extract_tables.py               │
    │                                   ▼
    ├── [academic-paper-translation] ──→  翻译内容用于双语PPT
    │   extract_paper_text.py
    │   translate_paper.py              │  可选（仅当需要双语PPT时）
    │   → 逐段翻译                      │
    │                                   ▼
    ├── [paper-analysis] ──────────────→  分析结果用于内容组织
    │   analyze_paper.py
    │                                   ▼
    └── [academic-ppt] ────────────────→  最终输出
        extract_paper_for_ppt.py
        paper_ppt.py --figures-dir ./paper_figures
        → 组会汇报PPT.pptx
```

### 快捷方式：全流程一键执行

```bash
# ========== 完整PPT制作工作流 ==========
PAPER="paper.pdf"
NAME=$(basename "$PAPER" .pdf)

# 1. 提取图表（用于PPT插图）
python ../extract-picture/scripts/extract_figures.py "$PAPER" -o "${NAME}_figures"
python ../extract-picture/scripts/extract_tables.py "$PAPER" -o "${NAME}_tables"

# 2. 分析论文结构
python ../paper-analysis/scripts/analyze_paper.py "$PAPER" -o "${NAME}_analysis.json"

# 3. 提取PPT结构
python scripts/extract_paper_for_ppt.py "$PAPER" -o "${NAME}_ppt_data.json"

# 4. 生成PPT（自动插入图表）
echo "编辑 ${NAME}_ppt_data.json 调整内容后执行："
echo "  python scripts/paper_ppt.py ${NAME}_ppt_data.json --figures-dir ${NAME}_figures -o ${NAME}_组会汇报.pptx"
```

---

## 幻灯片结构说明

`extract_paper_for_ppt.py` 输出的JSON包含以下幻灯片类型：

| 类型 | 说明 | 内容来源 |
|------|------|----------|
| `title` | 标题页 | 论文元信息 |
| `outline` | 目录页 | 检测到的章节 |
| `content` | 内容页 | 各章节文本（自动拆分长文本为子页） |
| `ending` | 总结思考页 | 预设引导问题 |
| `qa` | Q&A致谢页 | 固定内容 |

可直接编辑JSON文件调整：
- 幻灯片顺序和内容
- `subslides` 数组（控制长文本分页）
- `key_points` 中的贡献概括
- `bilingual` + `original` + `translation`（启用双语模式）
- `figure_hint`（指定对应图片关键词，用于自动插图）

## 标准PPT结构

参考 [references/presentation_guide.md](references/presentation_guide.md) 中的幻灯片结构指南。标准组会汇报建议包含：

1. **标题页** — 论文标题、作者、出处
2. **目录** — 汇报纲要
3. **研究背景与动机** — 为什么做这个研究？
4. **相关工作** — 现有方法的不足
5. **核心方法** — 论文的创新点和技术细节
6. **实验与分析** — 数据集、结果、消融实验
7. **结论与思考** — 优缺点 + 个人启发
8. **Q&A** — 致谢

## 高级定制

### PPT生成后优化

1. 在 PowerPoint/WPS 中手动微调布局和字体
2. 补充从论文中提取的图片（使用 `--figures-dir` 参数自动插入）
3. 调整动画和过渡效果
4. 添加备注（演讲提示）

## 相关技能

| 技能 | 目录 | 在本流程中的角色 |
|------|------|-----------------|
| `extract-picture` | `../extract-picture/` | **素材提供**: 提取图表供PPT插入 |
| `academic-paper-translation` | `../academic-paper-translation/` | **内容提供**: 翻译结果用于双语PPT |
| `paper-analysis` | `../paper-analysis/` | **参考**: 分析结果指导PPT内容组织 |
| `formula2latex` | `../formula2latex/` | **可选**: 提取公式渲染到PPT中 |

## 依赖安装

```bash
# 快速版（python-pptx）
pip install python-pptx PyMuPDF pdfplumber pypdf

# 图片插入需安装 Pillow
pip install Pillow

# 精美版（html2pptx + 图标库）
npm install -g pptxgenjs playwright sharp react-icons react react-dom
```
