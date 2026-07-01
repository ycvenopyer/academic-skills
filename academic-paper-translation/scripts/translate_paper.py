#!/usr/bin/env python3
"""
论文逐句中英对照翻译助手
输入已提取的论文文本，输出中英对照翻译结果（Markdown格式）。

用法:
  python translate_paper.py input.txt [--output output.md] [--mode paragraph|sentence]
"""

import argparse
import os
import re
from pathlib import Path


def parse_paper_text(text_path: str, mode: str = "paragraph") -> list[dict]:
    """
    解析提取的论文文本，返回结构化章节列表。
    mode="paragraph": 每章以段落为单位
    mode="sentence": 每章以句子为单位（更精细对照）
    每章: {"title": str, "segments": [str, ...]}
    """
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []
    lines = content.split('\n')
    current_title = "Header"
    current_segments = []
    current_buffer = []

    for line in lines:
        # 检测章节标题
        heading_match = re.match(r'^#+\s+(.+)$', line.strip())
        if heading_match:
            if current_segments:
                sections.append({"title": current_title, "segments": current_segments})
                current_segments = []
            current_title = heading_match.group(1)
            continue

        # 检测页面标记
        if re.match(r'^=====\s*第\s*\d+\s*页\s*=====$', line.strip()):
            continue

        # 空行 = 段落分隔
        if not line.strip():
            if current_buffer:
                para = '\n'.join(current_buffer).strip()
                if para:
                    if mode == "sentence":
                        # 按句子拆分
                        sentences = re.split(r'(?<=[.?!])\s+', para)
                        current_segments.extend(s for s in sentences if s.strip())
                    else:
                        current_segments.append(para)
                current_buffer = []
            continue

        current_buffer.append(line.rstrip())

    if current_buffer:
        para = '\n'.join(current_buffer).strip()
        if para:
            if mode == "sentence":
                sentences = re.split(r'(?<=[.?!])\s+', para)
                current_segments.extend(s for s in sentences if s.strip())
            else:
                current_segments.append(para)

    if current_segments:
        sections.append({"title": current_title, "segments": current_segments})

    return sections


def main():
    parser = argparse.ArgumentParser(description="论文翻译助手")
    parser.add_argument("input", help="输入文本文件路径（从 extract_paper_text.py 输出）")
    parser.add_argument("--output", "-o", default=None, help="输出翻译文件路径")
    parser.add_argument("--mode", choices=["paragraph", "sentence"], default="paragraph",
                        help="翻译粒度: paragraph（段级，默认）| sentence（句级）")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        return

    if args.output is None:
        args.output = Path(args.input).stem + "_translated.md"

    sections = parse_paper_text(args.input, args.mode)

    # 输出翻译模板
    total_segments = sum(len(s["segments"]) for s in sections)
    seg_label = "句子" if args.mode == "sentence" else "段落"

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("# 论文中英对照翻译\n\n")
        f.write(f"> 来源: {args.input}\n")
        f.write(f"> 翻译粒度: {'段落级' if args.mode == 'paragraph' else '句子级'}\n")
        f.write(f"> 总{seg_label}数: {total_segments}\n\n")
        f.write("---\n\n")

        for sec in sections:
            f.write(f"## {sec['title']}\n\n")
            for i, seg in enumerate(sec["segments"]):
                if not seg.strip():
                    continue
                seg_type = "句子" if args.mode == "sentence" else "段落"
                f.write(f"### {seg_type} {i+1}\n\n")
                f.write("**原文：**\n\n")
                f.write(f"{seg}\n\n")
                f.write("**译文：**\n\n")
                f.write(f"<!-- TODO: 在此填写翻译 -->\n\n")
                f.write("---\n\n")

    print(f"翻译模板已生成: {args.output}")
    print(f"共 {len(sections)} 个章节，{total_segments} 个{seg_label}待翻译")
    print("\n提示：请在 '译文：' 下方的 <!-- TODO --> 位置逐段填写翻译。")


if __name__ == "__main__":
    main()
