#!/usr/bin/env python3
"""
将 Markdown 文档批量转换为 PDF
使用 pandoc 进行转换
"""
import os
import subprocess
from pathlib import Path

# 目录配置
INPUT_DIR = Path('data/transcripts')
OUTPUT_DIR = Path('data/pdf')

def convert_md_to_pdf(md_file: Path, output_dir: Path):
    """使用 pandoc 将 Markdown 转换为 PDF"""
    
    # 输出文件名
    pdf_file = output_dir / f"{md_file.stem}.pdf"
    
    # pandoc 命令
    # 使用 wkhtmltopdf 引擎，更好支持中文
    cmd = [
        'pandoc',
        str(md_file),
        '-o', str(pdf_file),
        '--pdf-engine=xelatex',
        '-V', 'CJKmainfont=PingFang SC',  # macOS 中文字体
        '-V', 'geometry:margin=2cm',
        '-V', 'fontsize=11pt',
        '--wrap=auto',
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            return True, pdf_file
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "转换超时"
    except Exception as e:
        return False, str(e)


def convert_md_to_html_pdf(md_file: Path, output_dir: Path):
    """备选方案：先转HTML再用浏览器打印PDF"""
    
    html_file = output_dir / f"{md_file.stem}.html"
    
    # 读取 Markdown 内容
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单的 HTML 模板
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{md_file.stem}</title>
    <style>
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
            font-size: 14px;
        }}
        h1 {{ font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ font-size: 18px; color: #444; margin-top: 30px; }}
        p {{ margin: 15px 0; text-align: justify; }}
        strong {{ color: #2c5aa0; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 30px 0; }}
    </style>
</head>
<body>
"""
    
    # 简单的 Markdown 到 HTML 转换
    import re
    
    # 转换标题
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # 转换粗体
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    
    # 转换分隔线
    content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)
    
    # 转换段落
    paragraphs = content.split('\n\n')
    html_content = ""
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            html_content += f"<p>{p}</p>\n"
        else:
            html_content += p + "\n"
    
    html_template += html_content + "\n</body>\n</html>"
    
    # 保存 HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return html_file


def html_to_pdf(html_file: Path) -> Path:
    """使用 wkhtmltopdf 将 HTML 转换为 PDF"""
    pdf_file = html_file.with_suffix('.pdf')
    
    cmd = [
        'wkhtmltopdf',
        '--encoding', 'UTF-8',
        '--page-size', 'A4',
        '--margin-top', '20mm',
        '--margin-bottom', '20mm',
        '--margin-left', '15mm',
        '--margin-right', '15mm',
        '--quiet',
        str(html_file),
        str(pdf_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and pdf_file.exists():
            return pdf_file
    except Exception as e:
        pass
    
    return None


def main():
    """主函数"""
    print("=" * 70)
    print("📄 将 Markdown 文档转换为 PDF")
    print("=" * 70)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 获取所有 Markdown 文件
    md_files = sorted(INPUT_DIR.glob('*.md'))
    print(f"\n📂 找到 {len(md_files)} 个 Markdown 文件")
    
    success_count = 0
    fail_count = 0
    html_count = 0
    
    for i, md_file in enumerate(md_files, 1):
        print(f"\n[{i}/{len(md_files)}] {md_file.name[:50]}...")
        
        # 先生成 HTML
        try:
            html_file = convert_md_to_html_pdf(md_file, OUTPUT_DIR)
            
            # 使用 wkhtmltopdf 转换为 PDF
            pdf_file = html_to_pdf(html_file)
            
            if pdf_file and pdf_file.exists():
                print(f"  ✅ PDF: {pdf_file.name}")
                success_count += 1
                # 删除中间 HTML 文件
                html_file.unlink()
            else:
                print(f"  📄 HTML: {html_file.name} (PDF转换失败)")
                html_count += 1
                
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            fail_count += 1
    
    # 汇总
    print("\n" + "=" * 70)
    print("📊 转换完成！")
    print("=" * 70)
    print(f"  ✅ PDF 成功: {success_count} 个")
    print(f"  📄 HTML 备选: {html_count} 个")
    print(f"  ❌ 失败: {fail_count} 个")
    print(f"  📁 输出目录: {OUTPUT_DIR}")
    
    # 列出生成的文件
    print("\n📄 生成的文件:")
    for f in sorted(OUTPUT_DIR.glob('*')):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")


if __name__ == '__main__':
    main()