#!/usr/bin/env python3
"""
论文PDF表格提取工具
从PDF中提取表格数据，支持导出为 CSV、Excel 和 Markdown 格式。

用法:
  python extract_tables.py input.pdf [--output-dir ./tables] [--format csv|xlsx|md|all]
"""

import argparse
import os
import sys
import re
from pathlib import Path


def safe_filename(name: str) -> str:
    """将字符串转为安全的文件名"""
    return re.sub(r'[\\/*?:"<>|]', "_", name.strip())


def extract_tables_pdfplumber(pdf_path: str) -> list[dict]:
    """使用 pdfplumber 提取表格"""
    import pdfplumber
    import pandas as pd

    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:  # 至少需要表头+一行数据
                    continue

                # 清理空行
                table = [row for row in table if any(cell is not None for cell in row)]

                if len(table) < 2:
                    continue

                header = [str(c).strip() if c else "" for c in table[0]]
                data_rows = []
                for row in table[1:]:
                    data_rows.append([str(c).strip() if c else "" for c in row])

                # 尝试从周围文本获取标题
                page_text = page.extract_text() or ""
                caption = ""
                caption_match = re.search(
                    rf'Table\s*(\d+(?:\.\d+)?)[\s.:]*([^\n]*)',
                    page_text, re.IGNORECASE
                )
                if caption_match:
                    caption = f"Table {caption_match.group(1)}: {caption_match.group(2).strip()}"

                df = pd.DataFrame(data_rows, columns=header)
                all_tables.append({
                    "page": page_num + 1,
                    "index": table_idx + 1,
                    "header": header,
                    "data": data_rows,
                    "caption": caption,
                    "dataframe": df,
                    "rows": len(data_rows),
                    "cols": len(header),
                })

    return all_tables


def extract_tables_camelot(pdf_path: str) -> list[dict]:
    """使用 camelot 提取表格（适合有明确边框的表格）"""
    import camelot
    import pandas as pd

    all_tables = []

    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
    except Exception:
        try:
            tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
        except Exception as e:
            print(f"camelot 提取失败: {e}")
            return []

    for i, table in enumerate(tables):
        df = table.df
        if df.shape[0] < 2:
            continue

        header = df.iloc[0].tolist()
        data = df.iloc[1:].values.tolist()

        all_tables.append({
            "page": table.parsing_report.get("page", 0),
            "index": i + 1,
            "header": header,
            "data": [[str(c).strip() for c in row] for row in data],
            "caption": "",
            "dataframe": df,
            "rows": len(data),
            "cols": len(header),
            "accuracy": table.parsing_report.get("accuracy", 0),
        })

    return all_tables


def save_tables(tables: list[dict], output_dir: str, formats: list[str]):
    """保存表格为指定格式"""
    import pandas as pd

    if not tables:
        print("没有找到表格")
        return

    # 生成清单
    manifest_path = os.path.join(output_dir, "_tables_manifest.md")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# 表格提取清单\n\n")
        f.write(f"| 序号 | 页面 | 行数 | 列数 | 标题 |\n")
        f.write(f"|------|------|------|------|------|\n")
        for i, tbl in enumerate(tables):
            caption = tbl.get("caption", "") or f"Table (第{tbl['page']}页)"
            f.write(f"| {i+1} | {tbl['page']} | {tbl['rows']} | {tbl['cols']} | {caption[:40]} |\n")

        f.write(f"\n> 共提取 {len(tables)} 个表格\n")

    for i, tbl in enumerate(tables):
        caption_prefix = safe_filename(tbl.get("caption", "") or f"table_p{tbl['page']}_{i+1}")
        base = os.path.join(output_dir, f"table_{i+1:02d}_{caption_prefix[:30]}")

        if "csv" in formats:
            tbl["dataframe"].to_csv(f"{base}.csv", index=False, encoding='utf-8-sig')
            print(f"  CSV: {base}.csv")

        if "xlsx" in formats:
            tbl["dataframe"].to_excel(f"{base}.xlsx", index=False)
            print(f"  XLSX: {base}.xlsx")

        if "md" in formats:
            md_path = f"{base}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                if tbl["caption"]:
                    f.write(f"> {tbl['caption']}\n\n")
                f.write(f"| {' | '.join(tbl['header'])} |\n")
                f.write(f"|{' | '.join(['---'] * len(tbl['header']))} |\n")
                for row in tbl["data"]:
                    f.write(f"| {' | '.join(row)} |\n")
            print(f"  MD: {base}.md")

    print(f"\n清单: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="论文PDF表格提取工具")
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument("--output-dir", "-o", default=None, help="输出目录")
    parser.add_argument("--format", "-f", default="all",
                        help="输出格式: csv, xlsx, md, all（默认 all，用逗号分隔多个格式）")
    parser.add_argument("--engine", choices=["pdfplumber", "camelot"], default="pdfplumber",
                        help="提取引擎（pdfplumber通用，camelot适合带边框表格）")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    if args.output_dir is None:
        args.output_dir = Path(args.input).stem + "_tables"

    os.makedirs(args.output_dir, exist_ok=True)

    formats = ["csv", "xlsx", "md"] if args.format == "all" else args.format.split(",")

    print(f"正在从 {args.input} 提取表格...")
    print(f"输出目录: {args.output_dir}")
    print(f"引擎: {args.engine}")

    if args.engine == "pdfplumber":
        tables = extract_tables_pdfplumber(args.input)
    else:
        tables = extract_tables_camelot(args.input)

    print(f"提取了 {len(tables)} 个表格")
    save_tables(tables, args.output_dir, formats)

    print(f"\n✅ 提取完成！文件保存在: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
