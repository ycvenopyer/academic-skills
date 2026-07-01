---
name: academic-paper-translation
description: 学术论文逐字逐句中英对照翻译。当用户需要将英文学术论文完整翻译为中文时使用。支持：段落级逐段翻译、句子级逐句翻译、术语一致性检查、原文-译文精确对照。适用于论文精读、论文汇报准备、毕业论文翻译等场景。触发词："翻译论文"、"论文翻译"、"逐字逐句翻译"。
---

# 学术论文逐字逐句翻译

## 翻译流程

### 第1步：提取论文文本

```bash
# 普通电子版PDF（推荐）
python scripts/extract_paper_text.py paper.pdf --engine pdfplumber -o paper_extracted.txt

# 扫描版PDF（需OCR）
python scripts/extract_paper_text.py paper.pdf --ocr --lang eng -o paper_extracted.txt
```

### 第2步：生成翻译模板

```bash
python scripts/translate_paper.py paper_extracted.txt -o paper_translation.md

# 句子级翻译（更精细的对照）
python scripts/translate_paper.py paper_extracted.txt --mode sentence -o paper_translation.md
```

### 第3步：逐段翻译（由 Claude 完成）

对提取的每个段落/句子，按以下格式输出中英对照：

```markdown
**原文：**
[英文原文]

**译文：**
[中文译文]

---

**术语说明：**
- [术语1] → [译法说明]
```

---

## 🔗 跨技能调用 — 翻译前准备

翻译前，建议先调用 **extract-picture** 提取论文中的图片和表格。这能让翻译过程中直接引用图表的实际内容，确保`如图1所示`、`如表2所示`这类指代在翻译中准确对应。

### 调用 extract-picture 提取图表

```bash
# 进入项目的 extract-picture 技能目录执行（或使用完整路径）
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./paper_figures
python ../extract-picture/scripts/extract_tables.py paper.pdf -o ./paper_tables

# 查看提取的图表清单
cat ./paper_figures/_manifest.md
```

提取后，在翻译 **Figure/Table 标题** 时可参考实际图片内容：

```markdown
**原文：**
As shown in Figure 3, the proposed architecture consists of three main components...

**译文：**
如图3所示，本文提出的架构由三个主要组件组成...

**图3说明：** (来自 extract-picture 提取结果)
→ Figure 3: Overall architecture of the proposed model
→ （整体架构图，展示了编码器-解码器结构）
```

### 调用 extract-picture 提取表格用于翻译

表格翻译时，可直接引用提取的 Markdown 表格：

```bash
# 查看提取的表格
cat ./paper_tables/table_01_*.md
```

翻译后的表格格式：
```markdown
**原文表格（Table 1）：**
| Method | Accuracy | F1 Score |
|--------|----------|----------|
| Baseline | 85.2 | 83.1 |
| Ours | 91.5 | 89.7 |

**译文：**
| 方法 | 准确率 | F1 分数 |
|------|--------|---------|
| 基线方法 | 85.2 | 83.1 |
| 本文方法 | 91.5 | 89.7 |
```

---

## 🔗 跨技能调用 — 翻译后生成双语PPT

翻译完成后，可调用 **academic-ppt** 制作**中英双语组会汇报PPT**。

### 为学术PPT提供翻译后的内容

```bash
# 1. 先用 academic-ppt 提取论文结构
python ../academic-ppt/scripts/extract_paper_for_ppt.py paper.pdf -o paper_ppt_data.json

# 2. 编辑JSON，在每页嵌入中英文对照内容
#    （在 slide.content 中同时保留原文和译文）
```

编辑 `paper_ppt_data.json`，在幻灯片内容中嵌入双语对照：

```json
{
  "slides": [
    {
      "type": "content",
      "title": "Method (方法)",
      "content": "原文: We propose a novel architecture...\n译文: 本文提出了一种新颖的架构...",
      "bilingual": true
    }
  ]
}
```

### 生成中英双语PPT

```bash
# 直接生成 PPTX
python ../academic-ppt/scripts/paper_ppt.py paper_ppt_data.json -o 论文汇报_中英双语.pptx
```

PPT中每页的典型双语布局：
- 左侧栏：英文原文（较小字号，灰色）
- 右侧栏：中文译文（较大字号，深色）
- 底部：从 extract-picture 提取的图表

---

## 🌐 多技能组合工作流

### 完整翻译工作流（推荐顺序）

```
paper.pdf
    │
    ├── [extract-picture] ─────────────┐
    │   python extract_figures.py       │  翻译前获取图表上下文
    │   python extract_tables.py        │
    │                                   ▼
    ├── [academic-paper-translation] ──→  翻译中引用图表内容
    │   python extract_paper_text.py
    │   python translate_paper.py
    │   → 逐段翻译（Claude）
    │                                   ▼
    └── [academic-ppt] ────────────────→  翻译后生成双语PPT
        python extract_paper_for_ppt.py
        python paper_ppt.py
```

### 快捷方式：全流程一键执行

```bash
# ========== 完整翻译+PPT工作流 ==========
# 0. 设置变量
PAPER="paper.pdf"
NAME=$(basename "$PAPER" .pdf)

# 1. 提取图表（extract-picture）
python ../extract-picture/scripts/extract_figures.py "$PAPER" -o "${NAME}_figures"
python ../extract-picture/scripts/extract_tables.py "$PAPER" -o "${NAME}_tables"

# 2. 提取文本并翻译（academic-paper-translation）
python scripts/extract_paper_text.py "$PAPER" -o "${NAME}_extracted.txt"
python scripts/translate_paper.py "${NAME}_extracted.txt" -o "${NAME}_translation.md"
echo "✅ 文本已提取，请在 ${NAME}_translation.md 中逐段翻译"

# 3. 生成PPT结构（academic-ppt）
python ../academic-ppt/scripts/extract_paper_for_ppt.py "$PAPER" -o "${NAME}_ppt_data.json"
echo "✅ PPT结构已生成，编辑 ${NAME}_ppt_data.json 加入翻译内容后运行："
echo "   python ../academic-ppt/scripts/paper_ppt.py ${NAME}_ppt_data.json -o ${NAME}_汇报.pptx"
```

---

## 翻译规范

翻译时请遵循 [references/translation_guide.md](references/translation_guide.md) 中的规范。

关键要求：
- **逐字逐句对照**：每句原文都紧跟对应译文
- **术语一致性**：全篇统一术语译法
- **数学公式**：LaTeX 公式原样保留
- **参考文献**：`[1]`, `(Author, 2020)` 等引用格式不变
- **图表引用**：`Figure 3` → `图3`，`Table 2` → `表2`

## 处理特殊内容

### 算法/伪代码
```markdown
**原文（Algorithm 1）：**
```
Input: dataset D, learning rate η
for epoch = 1 to T do
    ...
```

**译文：**
```
输入：数据集 D，学习率 η
对于 epoch = 1 到 T 执行：
    ...
```
```

### 表格
将表格转为 Markdown 表格格式，保留表头与数据对应关系，表头可译为中文。

### 图表中的文字
提取图片中的文字时，在图片下方以注释形式提供图中文字的翻译。

## 输出文件结构

```
paper_translated.md
├── # 论文中英对照翻译
├── > 元信息（来源、粒度等）
├── ## Abstract（摘要）
│   ├── 段落 1: 原文 ↔ 译文
│   └── 段落 2: 原文 ↔ 译文
├── ## Introduction（引言）
│   └── ...
├── ## Method（方法）
│   └── ...
└── ## ...（后续章节）
```

## 翻译后质量检查清单

- [ ] 所有段落/句子已完成翻译（无 `<!-- TODO -->` 残留）
- [ ] 关键术语全文翻译一致
- [ ] 数学公式、代码片段完整保留
- [ ] 参考文献引用格式正确
- [ ] 专有名词首次出现时附有英文原文
- [ ] 图表引用（Figure/Table）已统一译为中文
- [ ] 提取的图片和表格已用于翻译上下文参考

## 相关技能

| 技能 | 目录 | 在本流程中的角色 |
|------|------|-----------------|
| `extract-picture` | `../extract-picture/` | **前置**: 提取图表供翻译参考 |
| `academic-ppt` | `../academic-ppt/` | **后置**: 用双语内容生成汇报PPT |
| `formula2latex` | `../formula2latex/` | **可选**: 翻译公式为LaTeX |
| `paper-analysis` | `../paper-analysis/` | **可选**: 翻译前先分析论文结构 |
