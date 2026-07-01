# OpenSkill

学术研究工具集 — 5个 Claude Code 技能，覆盖论文从阅读到汇报的全流程。
技能之间可以灵活组合，形成完整的工作流。

## 🧩 技能概览

| 技能 | 目录 | 一句话功能 |
|------|------|-----------|
| 📖 **论文翻译** | `academic-paper-translation/` | 逐字逐句中英对照翻译 |
| 🖼️ **图片表格提取** | `extract-picture/` | PDF图片提取、表格导出为CSV/Excel/MD |
| 📊 **组会汇报PPT** | `academic-ppt/` | 论文内容自动分析与PPT生成(含双语) |
| ∑ **公式转LaTeX** | `formula2latex/` | 公式图片OCR识别为LaTeX代码 |
| 🔍 **论文分析** | `paper-analysis/` | 论文结构化分析与10维度深度解读 |

## 🔗 技能间协作

```
extract-picture ──图表/表格──→  academic-paper-translation（翻译参考）
                              ──→  academic-ppt（PPT插图）
                              ──→  formula2latex（筛选公式）

academic-paper-translation ──→  academic-ppt（双语PPT内容）

paper-analysis ──→  academic-ppt（分析结果指导PPT内容组织）
```

## 📋 典型工作流

| 场景 | 使用技能 | 参考文档 |
|------|---------|---------|
| 论文精读与翻译 | extract-picture + translation + formula2latex + analysis | [WORKFLOWS.md](WORKFLOWS.md#场景1论文精读与翻译基础) |
| 组会PPT制作 | extract-picture + analysis + academic-ppt | [WORKFLOWS.md](WORKFLOWS.md#场景2组会ppt制作标准) |
| 双语汇报PPT | extract-picture + translation + academic-ppt | [WORKFLOWS.md](WORKFLOWS.md#场景3双语汇报ppt进阶) |
| 深度分析+汇报 | 全部5个技能 | [WORKFLOWS.md](WORKFLOWS.md#场景4论文深度分析汇报完整) |

详见 [WORKFLOWS.md](WORKFLOWS.md) — 跨技能组合工作流参考文档。

## 🚀 快速开始

```bash
# 安装通用依赖
pip install pypdf pdfplumber PyMuPDF pandas openpyxl python-pptx Pillow

# 以组会PPT制作为例
cd academic-ppt
python scripts/extract_paper_for_ppt.py ../paper.pdf -o paper_ppt_data.json
python scripts/paper_ppt.py paper_ppt_data.json -o 组会汇报.pptx
```

每个技能目录下的 `SKILL.md` 有详细的使用说明和跨技能调用指引。
