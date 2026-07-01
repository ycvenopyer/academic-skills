#!/usr/bin/env python3
"""
公式图片转LaTeX代码工具
支持：
1. 直接处理公式截图（PNG/JPG）
2. 从PDF中裁剪公式区域后识别
3. 批量处理文件夹中的公式图片

用法:
  python formula_ocr.py image.png [--output formula.tex]
  python formula_ocr.py --pdf paper.pdf --page 3 --region "100,200,400,350"
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


def ocr_formula_image(image_path: str) -> str:
    """
    使用 LaTeX-OCR (pix2tex) 识别公式图片。
    如果 pix2tex 不可用，尝试其他替代方案。
    """
    try:
        from pix2tex.cli import LatexOCR
        from PIL import Image
        model = LatexOCR()
        img = Image.open(image_path)
        latex_code = model(img)
        return latex_code.strip()
    except ImportError:
        print("提示: pix2tex 库未安装，尝试使用简易方案...")
        return _fallback_ocr(image_path)


def _fallback_ocr(image_path: str) -> str:
    """
    备用方案：如果 pix2tex 不可用，提示用户安装。
    也可使用 pdfplumber 提取PDF中已有的LaTeX（如果PDF包含LaTeX源码）。
    """
    print("=" * 50)
    print("LaTeX-OCR (pix2tex) 未安装。")
    print("请执行以下命令安装：")
    print("  pip install pix2tex[api]")
    print("")
    print("或者使用在线方案：")
    print("  1. https://www.latexocr.com/  (在线LaTeX OCR)")
    print("  2. https://mathpix.com/        (Mathpix, 需注册)")
    print("=" * 50)
    return "% 请安装 pix2tex 后重试\n% pip install pix2tex[api]"


def extract_formula_from_pdf(pdf_path: str, page_num: int, region: str = None) -> list[dict]:
    """
    从PDF中提取公式区域。
    region格式: "x1,y1,x2,y2" (左上和右下坐标，单位: 像素，需根据DPI换算)
    """
    import fitz
    doc = fitz.open(pdf_path)

    if page_num < 1 or page_num > len(doc):
        print(f"错误: 页码超出范围（共{len(doc)}页）")
        return []

    page = doc[page_num - 1]

    results = []

    if region:
        # 裁剪指定区域
        coords = [float(c) for c in region.split(",")]
        rect = fitz.Rect(coords[0], coords[1], coords[2], coords[3])
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect)

        img_path = f"formula_page{page_num}_region.png"
        pix.save(img_path)
        results.append({
            "image": img_path,
            "page": page_num,
            "region": region,
        })
        print(f"已裁剪公式区域: {img_path}")
    else:
        # 提取页面上所有图片，尝试识别公式
        images = page.get_images(full=True)
        for idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_path = f"formula_page{page_num}_img{idx+1}.png"
            with open(img_path, "wb") as f:
                f.write(base_image["image"])
            results.append({
                "image": img_path,
                "page": page_num,
                "index": idx,
            })
            print(f"已提取图片: {img_path}")

    doc.close()
    return results


def process_folder(folder_path: str, output_dir: str = None) -> list[dict]:
    """批量处理文件夹中的公式图片"""
    import glob

    image_exts = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff"]
    image_files = []
    for ext in image_exts:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        image_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))

    image_files.sort()

    if not image_files:
        print(f"文件夹中没有找到图片: {folder_path}")
        return []

    if output_dir is None:
        output_dir = folder_path

    results = []
    for img_path in image_files:
        print(f"正在识别: {os.path.basename(img_path)}")
        latex = ocr_formula_image(img_path)

        # 保存每个公式的LaTeX
        tex_path = os.path.join(output_dir, Path(img_path).stem + ".tex")
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex)

        results.append({
            "image": img_path,
            "latex": latex,
            "output": tex_path,
        })
        print(f"  → {latex[:80]}...")

    return results


def main():
    parser = argparse.ArgumentParser(description="公式图片转LaTeX代码工具")
    parser.add_argument("input", nargs="?", default=None, help="输入图片路径或PDF路径")
    parser.add_argument("--output", "-o", default=None, help="输出LaTeX文件路径")
    parser.add_argument("--pdf", action="store_true", help="输入为PDF文件")
    parser.add_argument("--page", type=int, default=1, help="PDF页码（默认第1页）")
    parser.add_argument("--region", default=None,
                        help="PDF裁剪区域: x1,y1,x2,y2（像素坐标）")
    parser.add_argument("--folder", default=None,
                        help="批量处理文件夹中的所有公式图片")
    parser.add_argument("--all", "-a", action="store_true",
                        help="合并所有识别结果为单个LaTeX文件")

    args = parser.parse_args()

    # 批量处理文件夹
    if args.folder:
        output_dir = None
        if args.output:
            output_dir = os.path.dirname(args.output)
        results = process_folder(args.folder, output_dir)

        print(f"\n✅ 处理完成: 共识别 {len(results)} 个公式")
        for r in results:
            print(f"  {os.path.basename(r['image'])} → {os.path.basename(r['output'])}")
        return

    if not args.input:
        parser.print_help()
        print("\n错误: 请指定输入图片或PDF路径")
        sys.exit(1)

    # PDF模式
    if args.pdf or args.input.lower().endswith('.pdf'):
        if not os.path.exists(args.input):
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)

        print(f"从PDF提取公式: {args.input}")
        regions = extract_formula_from_pdf(args.input, args.page, args.region)

        if not regions:
            print("未提取到公式区域")
            return

        if args.region:
            # 只识别裁剪的区域
            img_path = regions[0]["image"]
            latex = ocr_formula_image(img_path)

            if args.output is None:
                args.output = Path(img_path).stem + ".tex"

            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(latex)

            print(f"\n✅ 识别结果:")
            print(f"   公式: {latex}")
            print(f"   已保存: {args.output}")
        else:
            # 对每个提取的图片运行OCR
            for r in regions:
                latex = ocr_formula_image(r["image"])
                tex_path = Path(r["image"]).stem + ".tex"
                with open(tex_path, 'w', encoding='utf-8') as f:
                    f.write(latex)
                print(f"  {r['image']} → {latex}")

    # 图片模式
    else:
        if not os.path.exists(args.input):
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)

        print(f"正在识别公式图片: {args.input}")
        latex = ocr_formula_image(args.input)

        if args.output is None:
            args.output = Path(args.input).stem + ".tex"

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(latex)

        print(f"\n✅ 识别结果:")
        print(f"   LaTeX: {latex}")
        print(f"   已保存: {args.output}")

        # 如果是合并模式，也追加到 all_formulas.tex
        if args.all:
            all_file = "all_formulas.tex"
            with open(all_file, 'a', encoding='utf-8') as f:
                f.write(f"\n% From: {os.path.basename(args.input)}\n")
                f.write(latex)
                f.write("\n")
            print(f"   已追加到: {all_file}")


if __name__ == "__main__":
    main()
