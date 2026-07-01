---
name: formula2latex
description: 论文公式图片转LaTeX代码。当用户需要将学术论文中的数学公式转换为可编辑的LaTeX代码时使用。支持：公式截图/照片识别为LaTeX、PDF中裁剪公式区域识别、批量处理公式图片、常见数学符号（希腊字母、运算符、矩阵）的LaTeX写法参考。触发词："公式转LaTeX"、"公式识别"、"LaTeX公式"、"公式OCR"、"识别公式"。
---

# 公式转LaTeX代码

## 识别流程

### 方案A：识别公式截图（最常用）

```bash
# 单张公式截图识别
python scripts/formula_ocr.py formula.png -o formula.tex

# 多张公式截图（合并到 all_formulas.tex）
python scripts/formula_ocr.py eq1.png --all
python scripts/formula_ocr.py eq2.png --all
```

### 方案B：从PDF中裁剪公式区域

```bash
# 先提取PDF第3页的某区域作为图片
# region格式: x1,y1,x2,y2（左上角和右下角坐标，推荐使用PDF查看器量取）
python scripts/formula_ocr.py paper.pdf --pdf --page 3 --region "100,200,500,350"
```

### 方案C：批量处理文件夹

```bash
python scripts/formula_ocr.py --folder ./formula_images/ --output ./latex_output/
```

---

## 🔗 跨技能调用

### 配合 extract-picture 批量识别公式

extract-picture 提取的图片中常包含数学公式，可筛选后批量识别：

```bash
# 1. 先用 extract-picture 提取论文中的所有图片
python ../extract-picture/scripts/extract_figures.py paper.pdf -o ./all_figures

# 2. 人工筛选出公式图片放入 ./formula_images/ 目录
mkdir -p ./formula_images
# （从 ./all_figures/ 中复制公式图片到 ./formula_images/）

# 3. 批量识别公式
python scripts/formula_ocr.py --folder ./formula_images/ -o ./latex_output/

# 4. 合并所有公式到单个文件
cat ./latex_output/*.tex > paper_formulas.tex
```

### 为 academic-ppt 提供公式渲染

```bash
# 1. 识别论文关键公式
python scripts/formula_ocr.py formula.png -o key_formula.tex

# 2. 将LaTeX代码嵌入PPT的JSON结构中
# 在 paper_ppt_data.json 的 content 字段中添加：
# "核心公式: $$E = mc^2$$"
```

### 配合 academic-paper-translation

翻译论文时遇到公式，用本技能提取LaTeX后原样保留在译文中：

```bash
# 翻译前提取公式，确保LaTeX代码准确
python scripts/formula_ocr.py paper.pdf --pdf --page 5 --region "200,300,600,400" -o formula_eq5.tex

# 在翻译模板中引用：
"""
**原文：**
The loss function is defined as: L = -∑ y log(ŷ)

**译文：**
损失函数定义为：$\mathcal{L} = -\sum y \log(\hat{y})$
"""
```

---

## 输出格式

识别结果保存为 `.tex` 文件，可直接在LaTeX文档中使用：

```latex
% formula.tex
E = mc^2
```

对于简单公式，也可以直接使用 `$...$` 内联或 `$$...$$` 块级插入LaTeX文档：

```latex
本文的核心公式为 $E = mc^2$，其中...
```

## 手动校正提示

OCR识别不完美，识别后请人工校正以下常见问题：

1. **下标/上标混淆** — `x_i` 和 `x^i` 可能被认错
2. **花体识别** — `\mathcal{L}` 可能被识别成普通 `L`
3. **括号层级** — 确保 `\left(` 和 `\right)` 成对出现
4. **多字符函数名** — `\max`, `\min`, `\arg` 等
5. **复杂矩阵** — 行列对齐可能出错

详见 [references/latex_reference.md](references/latex_reference.md) 中的LaTeX符号对照表。

## 相关技能

| 技能 | 目录 | 在本流程中的角色 |
|------|------|-----------------|
| `extract-picture` | `../extract-picture/` | **前置**: 提取PDF图片供筛选公式 |
| `academic-paper-translation` | `../academic-paper-translation/` | **消费方**: 翻译中嵌入LaTeX公式 |
| `academic-ppt` | `../academic-ppt/` | **消费方**: PPT中渲染公式 |
| `paper-analysis` | `../paper-analysis/` | **可选**: 分析公式密度和复杂度 |

## 依赖安装

```bash
# 核心依赖 - LaTeX OCR
pip install pix2tex[api]

# PDF处理
pip install PyMuPDF pillow

# 批量处理
pip install pandas
```

> **提示**: 如果 `pix2tex` 安装失败，可使用在线服务：
> - [LaTeX-OCR在线版](https://www.latexocr.com/)
> - [Mathpix Snip](https://mathpix.com/)（更精确，每月免费20次）
