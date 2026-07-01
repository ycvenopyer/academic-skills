#!/usr/bin/env python3
"""
论文PDF文本提取工具
支持普通PDF和扫描版PDF（OCR），保留段落结构和章节信息。
用法:
  python extract_paper_text.py input.pdf [--output output.txt] [--ocr] [--lang eng+chi_sim]
"""

import argparse
import os
import sys
import re
from pathlib import Path


def extract_text_pypdf(pdf_path: str) -> str:
    """使用 pypdf 提取文本（速度快，适合电子版PDF）"""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        pages_text.append(f"===== 第 {i+1} 页 =====\n{text}")
    return "\n\n".join(pages_text)


def extract_text_pdfplumber(pdf_path: str) -> str:
    """使用 pdfplumber 提取文本（保留布局更好）"""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            pages_text.append(f"===== 第 {i+1} 页 =====\n{text}")
    return "\n\n".join(pages_text)


def extract_text_ocr(pdf_path: str, lang: str = "eng+chi_sim") -> str:
    """使用 OCR 提取扫描版PDF文本"""
    from pdf2image import convert_from_path
    import pytesseract

    images = convert_from_path(pdf_path, dpi=300)
    pages_text = []
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image, lang=lang)
        pages_text.append(f"===== 第 {i+1} 页 =====\n{text}")
    return "\n\n".join(pages_text)


def detect_sections(text: str) -> list[dict]:
    """
    检测论文章节结构（Introduction, Related Work, Method, Experiment, Conclusion等）
    返回章节列表：[{"title": "...", "content": "...", "page": int}]
    """
    section_patterns = [
        r'^(?:第[一二三四五六七八九十]+章|[1-9]\d*\.?)\s*(Abstract|Introduction|Related\s*Work|Background|Methodology|Method|Approach|Experiment|Evaluation|Results|Discussion|Conclusion|References)',
        r'^(Abstract|Introduction|Related\s*Work|Background|Method|Proposed\s*Method|Methodology|Approach|Experiment|Experimental\s*Setup|Evaluation|Results|Discussion|Conclusion|References|Acknowledgments?)\s*$',
    ]

    lines = text.split('\n')
    sections = []
    current_section = {"title": "Header", "content": [], "page": 1}

    for line in lines:
        matched = False
        for pattern in section_patterns:
            m = re.match(pattern, line.strip(), re.IGNORECASE)
            if m:
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": m.group(1), "content": [], "page": len(sections) + 1}
                matched = True
                break
        if not matched:
            current_section["content"].append(line)

    if current_section["content"]:
        sections.append(current_section)

    return sections


def save_with_structure(text: str, output_path: str):
    """保存文本，保留页面标记和章节结构"""
    sections = detect_sections(text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 论文文本提取结果\n\n")
        for sec in sections:
            f.write(f"## {sec['title']}\n\n")
            f.write('\n'.join(sec['content']))
            f.write('\n\n')
    print(f"文本已保存到: {output_path}")
    print(f"检测到 {len(sections)} 个章节")


def main():
    parser = argparse.ArgumentParser(description="论文PDF文本提取工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出文本文件路径")
    parser.add_argument("--ocr", action="store_true", help="启用OCR（用于扫描版PDF）")
    parser.add_argument("--lang", default="eng+chi_sim", help="OCR语言（默认: eng+chi_sim）")
    parser.add_argument("--engine", choices=["pypdf", "pdfplumber"], default="pdfplumber", help="提取引擎")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    if args.output is None:
        args.output = Path(args.input).stem + "_extracted.txt"

    print(f"正在提取: {args.input}")

    if args.ocr:
        text = extract_text_ocr(args.input, args.lang)
    elif args.engine == "pypdf":
        text = extract_text_pypdf(args.input)
    else:
        text = extract_text_pdfplumber(args.input)

    save_with_structure(text, args.output)


if __name__ == "__main__":
    main()
