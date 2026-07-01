#!/usr/bin/env python3
"""
论文PDF图片提取工具
从PDF中提取所有图片，按页面组织，并尝试关联图片标题。

用法:
  python extract_figures.py input.pdf [--output-dir ./figures] [--min-size 100x100] [--format png|jpg]
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path


def extract_images_pymupdf(pdf_path: str, output_dir: str, min_width: int = 100, min_height: int = 100,
                           img_format: str = "png") -> list[dict]:
    """使用 PyMuPDF (fitz) 提取PDF中的图片"""
    import fitz
    doc = fitz.open(pdf_path)
    extracted = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)
        page_extracted = []

        for img_idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # 图片尺寸过滤
            if base_image["width"] < min_width or base_image["height"] < min_height:
                continue

            # 生成文件名
            output_ext = "png" if img_format == "png" else image_ext
            filename = f"page{page_num+1:03d}_img{img_idx+1:02d}.{output_ext}"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            page_extracted.append({
                "page": page_num + 1,
                "index": img_idx + 1,
                "filename": filename,
                "width": base_image["width"],
                "height": base_image["height"],
                "format": image_ext,
            })

        extracted.extend(page_extracted)

    doc.close()
    return extracted


def extract_images_pdfimages(pdf_path: str, output_dir: str) -> list[dict]:
    """使用 pdfimages (poppler) 提取图片（命令行工具）"""
    prefix = os.path.join(output_dir, "img")
    result = subprocess.run(
        ["pdfimages", "-all", pdf_path, prefix],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"pdfimages 错误: {result.stderr}")
        return []

    extracted = []
    for img_path in sorted(glob.glob(os.path.join(output_dir, "img-*"))):
        basename = os.path.basename(img_path)
        # 从文件名推断信息
        extracted.append({
            "filename": basename,
            "path": img_path,
        })

    return extracted


def extract_captions(pdf_path: str) -> list[dict]:
    """从PDF文本中提取图表标题（Figure/Table 标题）"""
    import pdfplumber
    import re

    captions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # 匹配 Figure 标题
            fig_matches = re.finditer(
                r'(?:Fig(?:ure)?\.?\s*(\d+(?:\.\d+)?)[\s.:]*([^\n]*))',
                text, re.IGNORECASE
            )
            for m in fig_matches:
                captions.append({
                    "type": "figure",
                    "number": m.group(1),
                    "text": m.group(2).strip(),
                    "page": page_num + 1,
                })

            # 匹配 Table 标题
            tbl_matches = re.finditer(
                r'(?:Table\s*(\d+(?:\.\d+)?)[\s.:]*([^\n]*))',
                text, re.IGNORECASE
            )
            for m in tbl_matches:
                captions.append({
                    "type": "table",
                    "number": m.group(1),
                    "text": m.group(2).strip(),
                    "page": page_num + 1,
                })

    return captions


def generate_manifest(images: list[dict], captions: list[dict], output_dir: str):
    """生成提取结果清单文件"""
    manifest_path = os.path.join(output_dir, "_manifest.md")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# 图片提取清单\n\n")
        f.write(f"| 序号 | 页面 | 文件名 | 宽度 | 高度 | 格式 |\n")
        f.write(f"|------|------|--------|------|------|------|\n")
        for i, img in enumerate(images):
            f.write(f"| {i+1} | {img.get('page', '?')} | {img['filename']} "
                    f"| {img.get('width', '?')} | {img.get('height', '?')} "
                    f"| {img.get('format', '?')} |\n")

        if captions:
            f.write("\n## 检测到的图表标题\n\n")
            for cap in captions:
                emoji = "📊" if cap["type"] == "table" else "🖼️"
                f.write(f"- {emoji} **{cap['type'].title()} {cap['number']}** "
                        f"(第{cap['page']}页): {cap['text']}\n")

        f.write("\n---\n")
        f.write(f"\n> 共提取 {len(images)} 张图片, {len(captions)} 个图表标题\n")

    print(f"清单已生成: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="论文PDF图片提取工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("--output-dir", "-o", default=None, help="输出目录")
    parser.add_argument("--min-size", default="100x100", help="最小图片尺寸 (宽x高，默认 100x100)")
    parser.add_argument("--format", choices=["png", "jpg"], default="png", help="输出图片格式")
    parser.add_argument("--engine", choices=["pymupdf", "pdfimages"], default="pymupdf",
                        help="提取引擎（pymupdf 更稳定，pdfimages 更全面）")
    parser.add_argument("--no-captions", action="store_true", help="不提取图表标题")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    if args.output_dir is None:
        args.output_dir = Path(args.input).stem + "_figures"

    os.makedirs(args.output_dir, exist_ok=True)

    min_w, min_h = map(int, args.min_size.split("x"))

    print(f"正在从 {args.input} 提取图片...")
    print(f"输出目录: {args.output_dir}")

    if args.engine == "pymupdf":
        images = extract_images_pymupdf(args.input, args.output_dir, min_w, min_h, args.format)
    else:
        images = extract_images_pdfimages(args.input, args.output_dir)

    print(f"提取了 {len(images)} 张图片")

    captions = []
    if not args.no_captions:
        captions = extract_captions(args.input)
        print(f"检测到 {len(captions)} 个图表标题")

        # 尝试匹配图片和标题
        if images and captions:
            print("\n⚠️ 注意：图片和标题的匹配需要人工确认")
            print("   建议打开图片文件，对照清单中的标题进行对应")

    generate_manifest(images, captions, args.output_dir)

    print(f"\n✅ 提取完成！文件保存在: {os.path.abspath(args.output_dir)}")
    print(f"   打开 _manifest.md 查看提取清单")


if __name__ == "__main__":
    main()
