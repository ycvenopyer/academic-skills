# OpenSkill 跨技能组合工作流参考

本文档描述如何组合使用 OpenSkill 中的 5 个技能完成复杂的学术研究任务。

## 技能总览

```
openskill/
├── academic-paper-translation/   论文逐字逐句翻译
├── extract-picture/              图片和表格提取
├── academic-ppt/                 组会汇报PPT制作
├── formula2latex/                公式转LaTeX
└── paper-analysis/               论文分析
```

## 技能间数据流

```
extract-picture ──→ 图片、表格数据 ──→  academic-paper-translation（翻译参考）
                                      ──→  academic-ppt（PPT插图）
                                      ──→  formula2latex（筛选公式）
                                      ──→  paper-analysis（分析参考）

academic-paper-translation ──→ 双语文本 ──→  academic-ppt（双语PPT）

paper-analysis ──→ 分析结论 ──→  academic-ppt（内容指导）

formula2latex ──→ LaTeX代码 ──→  academic-paper-translation（公式嵌入）
                              ──→  academic-ppt（PPT公式渲染）
```

---

## 工作流场景

### 场景1：论文精读与翻译（基础）

**目标**：完整理解一篇英文学术论文

```
Step 1: [extract-picture]      提取图表 → 直观理解核心图表
Step 2: [academic-paper-translation]  文本提取 + 逐句翻译
Step 3: [formula2latex]        提取关键公式 → 理解数学原理
Step 4: [paper-analysis]       结构化分析 → 全面掌握
```

```bash
# 一键执行
PAPER="paper.pdf"
N=$(basename "$PAPER" .pdf)

python extract-picture/scripts/extract_figures.py "$PAPER" -o "${N}_figures"
python extract-picture/scripts/extract_tables.py "$PAPER" -o "${N}_tables"
python academic-paper-translation/scripts/extract_paper_text.py "$PAPER" -o "${N}_extracted.txt"
python academic-paper-translation/scripts/translate_paper.py "${N}_extracted.txt" -o "${N}_translation.md"
python paper-analysis/scripts/analyze_paper.py "$PAPER" --depth deep -o "${N}_analysis.json"

echo "✅ 精读准备完成！"
echo "  - 图表: ${N}_figures/ 和 ${N}_tables/"
echo "  - 翻译模板: ${N}_translation.md（需逐段填写译文）"
echo "  - 分析数据: ${N}_analysis.json"
```

---

### 场景2：组会PPT制作（标准）

**目标**：快速生成组会汇报PPT

```
Step 1: [extract-picture]      提取图表 → PPT素材
Step 2: [paper-analysis]       分析论文 → PPT内容依据
Step 3: [academic-ppt]         生成PPT
```

```bash
PAPER="paper.pdf"
N=$(basename "$PAPER" .pdf)

python extract-picture/scripts/extract_figures.py "$PAPER" -o "${N}_figures"
python extract-picture/scripts/extract_tables.py "$PAPER" -o "${N}_tables"
python paper-analysis/scripts/analyze_paper.py "$PAPER" --depth standard -o "${N}_analysis.json"
python academic-ppt/scripts/extract_paper_for_ppt.py "$PAPER" -o "${N}_ppt_data.json"
python academic-ppt/scripts/paper_ppt.py "${N}_ppt_data.json" --figures-dir "${N}_figures" -o "${N}_汇报PPT.pptx"

echo "✅ PPT已生成: ${N}_汇报PPT.pptx"
```

---

### 场景3：双语汇报PPT（进阶）

**目标**：制作中英双语的组会汇报PPT

```
Step 1: [extract-picture]      提取图表 → PPT插图
Step 2: [academic-paper-translation]  翻译全文 → 双语内容
Step 3: [academic-ppt]         生成双语PPT
```

```bash
PAPER="paper.pdf"
N=$(basename "$PAPER" .pdf)

# 1. 提取图表
python extract-picture/scripts/extract_figures.py "$PAPER" -o "${N}_figures"

# 2. 提取文本并翻译
python academic-paper-translation/scripts/extract_paper_text.py "$PAPER" -o "${N}_extracted.txt"
python academic-paper-translation/scripts/translate_paper.py "${N}_extracted.txt" -o "${N}_translation.md"
echo "→ 请先在 ${N}_translation.md 中完成逐段翻译！"

# 3. 生成PPT结构
python academic-ppt/scripts/extract_paper_for_ppt.py "$PAPER" -o "${N}_ppt_data.json"

# 4. 编辑JSON：将翻译填入每页的 translation 字段，设置 bilingual: true
echo "→ 编辑 ${N}_ppt_data.json，为每页添加："
echo '  "bilingual": true,'
echo '  "original": "英文原文",'
echo '  "translation": "中文译文"'

# 5. 生成双语PPT
echo "→ 编辑完成后执行："
echo "  python academic-ppt/scripts/paper_ppt.py ${N}_ppt_data.json --figures-dir ${N}_figures -o ${N}_双语汇报.pptx"
```

---

### 场景4：论文深度分析汇报（完整）

**目标**：对论文进行深度分析并制作报告PPT（最完整流程）

```
Step 1: [extract-picture]      提取所有图表
Step 2: [formula2latex]        提取关键公式
Step 3: [academic-paper-translation]  翻译辅助理解
Step 4: [paper-analysis]       深度结构化分析（10维度）
Step 5: [academic-ppt]         结合分析结果制作PPT
```

---

### 场景5：公式驱动的技术复现准备

**目标**：从论文中提取所有公式，为复现工作做准备

```
Step 1: [extract-picture]      提取所有图片
Step 2: 人工筛选公式图片
Step 3: [formula2latex]        批量识别公式 → 收集所有LaTeX
Step 4: [academic-paper-translation]  翻译公式说明文字
```

```bash
PAPER="paper.pdf"
N=$(basename "$PAPER" .pdf)

python extract-picture/scripts/extract_figures.py "$PAPER" -o "${N}_figures" --min-size 200x200
echo "→ 人工筛选 ${N}_figures/ 中的公式图片到 ./formula_images/"
echo "→ 然后执行："
echo "  formula2latex/scripts/formula_ocr.py --folder ./formula_images/"
```

---

## 流程图解

### 技能调度关系图

```
                        ┌──────────────────┐
                        │  paper.pdf       │
                        └────────┬─────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
        ┌─────────────────┐ ┌──────────┐ ┌──────────────┐
        │ extract-picture │ │formula2- │ │ paper-       │
        │ (图表+表格提取) │ │latex     │ │ analysis     │
        └────────┬────────┘ │(公式识别) │ │ (结构化分析)  │
                 │          └──────────┘ └──────┬───────┘
                 ▼                              │
        ┌─────────────────┐                     │
        │ academic-paper- │                     │
        │ translation     │                     │
        │ (逐句翻译)      │                     │
        └────────┬────────┘                     │
                 │                              │
                 ▼                              ▼
        ┌──────────────────────────────────────────┐
        │             academic-ppt                 │
        │         (组会汇报PPT制作)                 │
        └──────────────────────────────────────────┘
```

### 调用路径速查表

| 发起技能 | 调用目标 | 用途 | 调用方式 |
|----------|---------|------|---------|
| `academic-paper-translation` | `extract-picture` | 翻译前提取图表参考 | `python ../extract-picture/scripts/extract_figures.py` |
| `academic-paper-translation` | `academic-ppt` | 翻译后生成双语PPT | `python ../academic-ppt/scripts/paper_ppt.py` |
| `academic-ppt` | `extract-picture` | PPT插图 | `python ../extract-picture/scripts/extract_figures.py` |
| `academic-ppt` | `paper-analysis` | 分析结果指导内容 | `python ../paper-analysis/scripts/analyze_paper.py` |
| `academic-ppt` | `academic-paper-translation` | 双语PPT内容 | 编辑JSON中 `bilingual` 字段 |
| `paper-analysis` | `extract-picture` | 分析参考图表 | `python ../extract-picture/scripts/extract_figures.py` |
| `paper-analysis` | `academic-paper-translation` | 翻译辅助理解 | `python ../academic-paper-translation/scripts/translate_paper.py` |
| `formula2latex` | `extract-picture` | 从提取的图片中筛公式 | `python ../extract-picture/scripts/extract_figures.py` |

---

## 最佳实践

### 目录组织规范

进行多技能协作时，建议按以下结构组织文件：

```
project/
├── paper.pdf                  # 原论文
├── _figures/                  # extract-picture 输出（图片）
├── _tables/                   # extract-picture 输出（表格）
├── _extracted.txt             # academic-paper-translation 提取文本
├── _translation.md            # academic-paper-translation 翻译结果
├── _analysis.json             # paper-analysis 分析结果
├── _ppt_data.json             # academic-ppt 幻灯片结构
└── _组会汇报.pptx             # 最终PPT输出
```

### 注意事项

1. **路径问题**：技能间的脚本调用使用 `../技能名/scripts/` 相对路径，确保从项目根目录或各技能目录执行时路径正确
2. **依赖安装**：每个技能都列出了所需依赖，使用前请确认已安装
3. **执行顺序**：部分技能有前后依赖关系（如PPT需要图表输出），请按工作流指示的顺序执行
4. **中间产物**：各脚本生成的JSON/TXT/MD文件是后续步骤的输入，请勿随意删除
