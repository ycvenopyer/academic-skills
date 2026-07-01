#!/usr/bin/env python3
"""
论文结构化分析工具
从PDF提取论文内容，生成结构化分析报告。
输出JSON格式的结构化数据，供Claude进一步分析。

用法:
  python analyze_paper.py input.pdf [--output analysis.json] [--depth basic|standard|deep]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extract_paper_text(pdf_path: str) -> tuple[str, dict]:
    """提取论文文本和元数据"""
    from pypdf import PdfReader
    import pdfplumber

    reader = PdfReader(pdf_path)
    meta = reader.metadata or {}

    meta_info = {
        "title": (meta.get("/Title") or "").strip(),
        "author": (meta.get("/Author") or "").strip(),
        "subject": (meta.get("/Subject") or "").strip(),
        "keywords": (meta.get("/Keywords") or "").strip(),
        "pages": len(reader.pages),
    }

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text += text + "\n\n"

    return full_text, meta_info


def analyze_basic(full_text: str) -> dict:
    """基础分析：论文基本信息"""
    lines = full_text[:5000].split('\n')
    abstract_start = -1
    abstract_end = -1

    for i, line in enumerate(lines):
        stripped = line.strip().lower()
        if re.match(r'^abstract\s*$', stripped):
            abstract_start = i
        elif abstract_start >= 0 and re.match(r'^(introduction|keywords?|index\s*terms)', stripped):
            abstract_end = i
            break

    abstract = ""
    if abstract_start >= 0 and abstract_end > abstract_start:
        abstract = '\n'.join(lines[abstract_start+1:abstract_end]).strip()

    # 统计词数
    words = re.findall(r'\b[a-zA-Z]+\b', full_text)
    word_count = len(words)

    # 统计页面
    page_count = full_text.count('\n\n') // 50 + 1

    return {
        "abstract": abstract[:2000],
        "word_count_approx": word_count,
        "page_count_approx": page_count,
        "has_abstract": bool(abstract),
    }


def analyze_structure(full_text: str) -> dict:
    """结构分析：论文章节结构"""
    lines = full_text.split('\n')

    # 常见章节标题
    section_patterns = [
        r'^(?:1[\.\s]|I\s)?\s*(Introduction|引言|绪论)\s*$',
        r'^(?:2[\.\s]|II\s)?\s*(Related\s*Work|Background|Preliminaries|相关工作|背景)\s*$',
        r'^(?:3[\.\s]|III\s)?\s*(Method(?:ology)?|Approach|Model|Architecture|Framework|Proposed\s*Method|方法|模型)\s*$',
        r'^(?:4[\.\s]|IV\s)?\s*(Experiment|Experimental\s*(?:Setup|Results)?|Evaluation|Results|实验|评估|结果)\s*$',
        r'^(?:5[\.\s]|V\s)?\s*(Discussion|Analysis|Analysis\s*and\s*Discussion|讨论|分析)\s*$',
        r'^(?:6[\.\s]|VI\s)?\s*(Conclusion|Conclusion\s*and\s*Future\s*Work|Summary|总结|结论)\s*$',
        r'^(?:7[\.\s]|VII\s)?\s*(References|参考文献)\s*$',
    ]

    sections_found = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in section_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                sections_found.append({
                    "line": i,
                    "title": stripped,
                    "level": "major",
                })
                break

    # 检测图表数量
    figure_count = len(re.findall(r'(?:Fig(?:ure)?\.?\s*\d+)', full_text, re.IGNORECASE))
    table_count = len(re.findall(r'(?:Table\s*\d+)', full_text, re.IGNORECASE))
    equation_count = len(re.findall(r'(?:Eq\.?\s*\d+|Equation\s*\d+)', full_text, re.IGNORECASE))
    citation_count = len(re.findall(r'\[[\d,\s-]+\]', full_text))

    return {
        "sections_detected": [s["title"] for s in sections_found],
        "section_count": len(sections_found),
        "figure_count": figure_count,
        "table_count": table_count,
        "equation_count": equation_count,
        "citation_count": citation_count,
    }


def analyze_methodology(full_text: str) -> dict:
    """方法学分析"""
    text_lower = full_text.lower()

    analysis = {
        "supervised": bool(re.search(r'\b supervised \b', text_lower)),
        "unsupervised": bool(re.search(r'\b unsupervised \b', text_lower)),
        "semi_supervised": bool(re.search(r'\b semi[-\s]?supervised \b', text_lower)),
        "reinforcement_learning": bool(re.search(r'\b reinforcement\s+learning \b', text_lower)) or bool(re.search(r'\b RL \b', text_lower)),
        "deep_learning": bool(re.search(r'\b deep\s+(?:learning|neural)\b', text_lower)),
        "transformer": bool(re.search(r'\b transformer\b', text_lower)),
        "cnn": bool(re.search(r'\b CNN\b', text_lower)) or bool(re.search(r'\b convolutional\b', text_lower)),
        "rnn": bool(re.search(r'\b RNN\b', text_lower)) or bool(re.search(r'\b recurrent\b', text_lower)),
        "attention": bool(re.search(r'\b attention\b', text_lower)),
        "generative": bool(re.search(r'\b GAN\b', text_lower)) or bool(re.search(r'\b generative\b', text_lower)) or bool(re.search(r'\b diffusion\b', text_lower)),
        "graph_neural_network": bool(re.search(r'\b GNN\b', text_lower)) or bool(re.search(r'\b graph\s+neural\b', text_lower)),
        "transfer_learning": bool(re.search(r'\b transfer\s+learning\b', text_lower)),
        "multi_task": bool(re.search(r'\b multi[-\s]?task\b', text_lower)),
        "few_shot": bool(re.search(r'\b few[-\s]?shot\b', text_lower)),
        "self_supervised": bool(re.search(r'\b self[-\s]?supervised\b', text_lower)),
    }

    # 检测训练相关
    training_info = {}
    dataset_match = re.search(r'(?:dataset|benchmark)\s*(?:is|are|contain|include|consist)[^.]*\.', full_text, re.IGNORECASE)
    if dataset_match:
        training_info["dataset_mentioned"] = dataset_match.group(0)[:200]

    # 检测评估指标
    metrics = re.findall(r'\b(accuracy|precision|recall|f1[-\s]?score|F1|BLEU|ROUGE|perplexity|RMSE|MAE|MSE|AUC|MAP|NDCG|mAP|IoU|PSNR|SSIM)\b', full_text, re.IGNORECASE)
    training_info["metrics"] = list(set(metrics))

    return {
        "techniques": analysis,
        "training_info": training_info,
        "technique_count": sum(1 for v in analysis.values() if v),
    }


def analyze_contributions(full_text: str) -> dict:
    """贡献点与实验结果分析"""
    contributions = []

    # 找贡献点
    contribution_patterns = [
        r'(?:our\s+(?:main\s+)?contribution[s]?(?:\s+are|\s+include|\s+can\s+be\s+summarized\s+as)?[:\s]*)([^.]*(?:\.|$))',
        r'(?:we\s+(?:propose|present|introduce|develop|design)\s+(?:a\s+|an\s+|the\s+)?(?:novel\s+|new\s+|first\s+)?)([^.]*(?:\.|$))',
        r'(?:this\s+paper\s+(?:proposes|presents|introduces|describes)\s+)([^.]*(?:\.|$))',
        r'(?:to\s+the\s+best\s+of\s+our\s+knowledge)[^.]*(?:\.|$)',
        r'(?:key\s+(?:contribution|idea|innovation|insight)s?[:\s]*)([^.]*(?:\.|$))',
    ]

    for pattern in contribution_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for m in matches:
            sentence = m.strip() if isinstance(m, str) else m[0].strip()
            if len(sentence) > 20:
                contributions.append(sentence)

    # 找SOTA比较
    sota_mentions = re.findall(
        r'(?:outperform|state[-\s]of[-\s]the[-\s]art|better\s+than|superior\s+to|improve|gain)[^.]*\d+(?:\.\d+)?[^.]*(?:%|\b)(?:[^.]*\.)',
        full_text, re.IGNORECASE
    )

    return {
        "contributions": contributions[:10],
        "sota_comparisons": sota_mentions[:5],
        "contribution_count": len(contributions),
    }


def analyze_paper(pdf_path: str, depth: str = "standard") -> dict:
    """完整的论文分析"""
    full_text, meta = extract_paper_text(pdf_path)

    if not full_text.strip():
        return {"error": "无法提取论文文本，可能为扫描版PDF，请使用OCR后再分析。"}

    analysis = {
        "metadata": meta,
        "basic": analyze_basic(full_text),
        "structure": analyze_structure(full_text),
    }

    if depth in ("standard", "deep"):
        analysis["methodology"] = analyze_methodology(full_text)
        analysis["contributions"] = analyze_contributions(full_text)

    return analysis


def main():
    parser = argparse.ArgumentParser(description="论文结构化分析工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出JSON文件路径")
    parser.add_argument("--depth", choices=["basic", "standard", "deep"], default="standard",
                        help="分析深度（basic: 基础信息, standard: 标准含方法论, deep: 完整分析）")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    if args.output is None:
        args.output = Path(args.input).stem + "_analysis.json"

    print(f"正在分析论文: {args.input}")
    print(f"分析深度: {args.depth}")

    analysis = analyze_paper(args.input, args.depth)

    if "error" in analysis:
        print(f"错误: {analysis['error']}")
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    meta = analysis["metadata"]
    basic = analysis["basic"]
    structure = analysis["structure"]

    print(f"\n✅ 分析完成！结果已保存: {args.output}")
    print(f"\n=== 分析摘要 ===")
    print(f"  标题: {meta.get('title', '未知')[:80]}")
    print(f"  作者: {meta.get('author', '未知')[:60]}")
    print(f"  关键词: {meta.get('keywords', '无')[:60]}")
    print(f"  页数: {meta.get('pages', '?')}")
    print(f"  预估词数: {basic.get('word_count_approx', 0)}")
    print(f"  有摘要: {'是' if basic.get('has_abstract') else '否'}")
    print(f"  章节数: {structure.get('section_count', 0)}")
    print(f"  图表: {structure.get('figure_count', 0)}张图, {structure.get('table_count', 0)}个表")
    print(f"  公式: {structure.get('equation_count', 0)}个")
    print(f"  参考文献: ~{structure.get('citation_count', 0)}篇")

    if args.depth in ("standard", "deep"):
        meth = analysis.get("methodology", {})
        contrib = analysis.get("contributions", {})
        print(f"  检测到技术关键词: {meth.get('technique_count', 0)}个")
        print(f"  贡献点: {contrib.get('contribution_count', 0)}个")

    print(f"\n💡 将分析结果JSON提供给Claude，获取更深入的论文解读。")


if __name__ == "__main__":
    main()
