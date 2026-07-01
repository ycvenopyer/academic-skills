#!/usr/bin/env python3
"""
论文PPT内容提取与结构化工具
从论文PDF中提取关键信息，生成适合PPT展示的结构化内容。
输出格式为JSON，供后续PPT生成脚本使用。

用法:
  python extract_paper_for_ppt.py input.pdf [--output paper_data.json] [--lang en|zh]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extract_paper_info(pdf_path: str) -> dict:
    """提取论文元信息和结构化内容"""
    from pypdf import PdfReader
    import pdfplumber

    reader = PdfReader(pdf_path)
    meta = reader.metadata or {}

    paper_info = {
        "title": (meta.get("/Title") or os.path.basename(pdf_path).replace(".pdf", "")).strip(),
        "authors": meta.get("/Author", "").strip(),
        "pages": len(reader.pages),
        "sections": [],
    }

    # 用 pdfplumber 提取带布局的文本
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += f"\n\n--- PAGE {i+1} ---\n\n{text}"

    paper_info["full_text"] = full_text

    # 检测章节结构
    section_keywords = [
        "abstract", "introduction", "related work", "background",
        "methodology", "method", "proposed", "approach",
        "experiment", "experimental", "evaluation", "results",
        "discussion", "conclusion", "reference"
    ]

    lines = full_text.split('\n')
    current_section = "header"
    current_content = []

    for line in lines:
        stripped = line.strip().lower().rstrip(':')
        if stripped in section_keywords or any(f" {kw}" in stripped or stripped.startswith(kw) for kw in section_keywords):
            if current_content:
                paper_info["sections"].append({
                    "title": current_section,
                    "content": '\n'.join(current_content).strip()
                })
            current_section = line.strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        paper_info["sections"].append({
            "title": current_section,
            "content": '\n'.join(current_content).strip()
        })

    return paper_info


def extract_key_points(text: str) -> dict:
    """提取论文关键要点"""
    result = {
        "problem": "",
        "motivation": "",
        "contribution": "",
        "method_summary": "",
        "key_results": [],
    }

    sections_text = text.lower()

    # 提取贡献点
    contributions = re.findall(
        r'(?:our\s+(?:main\s+)?contribution[s]?(?:\s+are|\s+include|\s+can\s+be\s+summarized\s+as)?[:\s]*)([^.]*(?:\.|$))',
        text, re.IGNORECASE
    )
    if contributions:
        result["contribution"] = '. '.join(c.strip() for c in contributions)

    # 提取实验结果关键词
    result_text = text[:10000]  # 只在前部分找
    result_lines = []
    for line in result_text.split('\n'):
        if any(kw in line.lower() for kw in ["achieve", "outperform", "improve", "state-of-the-art",
                                              "sota", "best", "accuracy", "f1-score", "bleu",
                                              "gain", "improvement", "significant"]):
            if len(line.strip()) > 20:
                result_lines.append(line.strip())

    result["key_results"] = result_lines[:10]

    return result


def generate_ppt_structure(paper_info: dict) -> list[dict]:
    """生成PPT幻灯片结构"""
    slides = []
    sections = paper_info.get("sections", [])
    text = paper_info.get("full_text", "")

    # 1. 标题页
    slides.append({
        "type": "title",
        "title": paper_info.get("title", "论文标题"),
        "subtitle": f"作者: {paper_info.get('authors', '未知')} | 共{paper_info.get('pages', 0)}页",
    })

    # 2. 目录页
    section_titles = [s["title"] for s in sections if s["title"] != "header" and "reference" not in s["title"].lower()]
    slides.append({
        "type": "outline",
        "title": "汇报提纲",
        "items": section_titles[:8],  # 最多8项
    })

    # 3. 研究背景/问题
    for sec in sections:
        sec_lower = sec["title"].lower()
        if any(kw in sec_lower for kw in ["abstract", "introduction", "background"]):
            content = sec["content"][:1500]
            slides.append({
                "type": "content",
                "title": sec["title"],
                "content": content,
                "subslides": _split_content(content, 800),
            })
            break

    # 4. 相关工作
    for sec in sections:
        if "related" in sec["title"].lower():
            slides.append({
                "type": "content",
                "title": sec["title"],
                "content": sec["content"][:1500],
                "subslides": _split_content(sec["content"], 800),
            })
            break

    # 5. 方法
    method_sections = [s for s in sections if any(kw in s["title"].lower()
                       for kw in ["method", "proposed", "approach", "methodology", "model", "architecture", "framework"])]
    if method_sections:
        for ms in method_sections[:2]:
            slides.append({
                "type": "content",
                "title": ms["title"],
                "content": ms["content"][:2000],
                "subslides": _split_content(ms["content"], 800),
            })

    # 6. 实验
    for sec in sections:
        sec_lower = sec["title"].lower()
        if any(kw in sec_lower for kw in ["experiment", "evaluation", "results"]):
            content = sec["content"]
            slides.append({
                "type": "content",
                "title": sec["title"],
                "content": content[:2000],
                "subslides": _split_content(content, 800),
            })
            break

    # 7. 结论
    for sec in sections:
        if "conclusion" in sec["title"].lower():
            slides.append({
                "type": "content",
                "title": sec["title"],
                "content": sec["content"][:1000],
            })
            break

    # 8. 讨论与思考
    slides.append({
        "type": "ending",
        "title": "总结与思考",
        "points": [
            "论文核心贡献是什么？",
            "方法的创新点在哪里？",
            "实验结论是否充分支持论点？",
            "对本人研究有什么启发？",
            "可能存在的问题或改进方向？",
        ]
    })

    # 9. Q&A
    slides.append({
        "type": "qa",
        "title": "谢谢！欢迎提问",
    })

    return slides


def _split_content(content: str, max_len: int = 800) -> list[str]:
    """将长内容拆分为多个子幻灯片的内容"""
    if len(content) <= max_len:
        return [content]

    parts = []
    sentences = content.replace('\n', ' ').split('. ')
    current = ""

    for sent in sentences:
        if len(current) + len(sent) < max_len:
            current += sent + ". "
        else:
            if current:
                parts.append(current.strip())
            current = sent + ". "

    if current:
        parts.append(current.strip())

    return parts


def main():
    parser = argparse.ArgumentParser(description="论文PPT内容提取工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出JSON文件路径")
    parser.add_argument("--lang", choices=["en", "zh"], default="zh", help="输出语言")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    if args.output is None:
        args.output = Path(args.input).stem + "_ppt_data.json"

    print(f"正在分析: {args.input}")
    paper_info = extract_paper_info(args.input)

    print(f"论文标题: {paper_info['title'][:80]}")
    print(f"检测到 {len(paper_info['sections'])} 个章节")

    key_points = extract_key_points(paper_info.get("full_text", ""))

    slides = generate_ppt_structure(paper_info)

    output_data = {
        "paper_info": {
            "title": paper_info["title"],
            "authors": paper_info["authors"],
            "pages": paper_info["pages"],
        },
        "key_points": key_points,
        "slides": slides,
        "slide_count": len(slides),
        "lang": args.lang,
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ PPT结构数据已保存: {args.output}")
    print(f"   共 {len(slides)} 张幻灯片")
    print(f"\n提示：")
    print(f"   1. 使用 `python paper_ppt.py {args.output}` 可直接生成PPT")
    print(f"   2. 编辑JSON文件可调整幻灯片结构和内容")
    print(f"   3. 配合 academic-ppt 技能的 html2pptx 流程使用效果最佳")


if __name__ == "__main__":
    main()
