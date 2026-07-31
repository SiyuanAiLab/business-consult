#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""
business-consult research — 研报风格 HTML 生成器
将 Markdown 报告转换为专业行业研究报告风格的单文件 HTML

用法：
  python3 generate_report.py <输入.md> [输出.html]

默认：
  输入：10-research-report.md（当前目录）
  输出：10-research-report.html
"""

import markdown
import re
import sys
import os


def generate(input_path, output_path=None):
    # 读取输入
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 自动推断输出文件名
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".html"

    # Strip frontmatter
    md_body = re.sub(r'^---\n.*?---\n', '', md_content, flags=re.DOTALL, count=1)

    # Convert wiki-links to plain text
    md_body = re.sub(r'\[\[(.*?)(?:\|(.*))?\]\]', lambda m: m.group(2) or m.group(1), md_body)

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'toc',
        'nl2br',
        'sane_lists',
        'smarty',
    ])

    html_body = md.convert(md_body)
    toc_html = md.toc

    # Extract title / author / date from frontmatter if present
    title = re.search(r'^title:\s*(.+)$', md_content, re.MULTILINE)
    title = title.group(1).strip() if title else "行业研究报告"
    author = re.search(r'^author:\s*(.+)$', md_content, re.MULTILINE)
    author = author.group(1).strip() if author else "Research Team"
    date = re.search(r'^date:\s*(.+)$', md_content, re.MULTILINE)
    date = date.group(1).strip() if date else ""

    # Professional research report CSS
    CSS = """
:root {
  --primary: #1a365d;
  --primary-light: #2c5282;
  --accent: #c53030;
  --bg: #ffffff;
  --bg-alt: #f7fafc;
  --bg-card: #edf2f7;
  --text: #1a202c;
  --text-secondary: #4a5568;
  --border: #e2e8f0;
  --border-strong: #cbd5e0;
  --radius: 6px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body {
  font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, "Times New Roman", serif;
  font-size: 15.5px; line-height: 1.75; color: var(--text); background: #f0f2f5;
}
.layout {
  display: flex; max-width: 1200px; margin: 0 auto; min-height: 100vh;
}
.sidebar {
  width: 260px; flex-shrink: 0; background: var(--bg);
  border-right: 1px solid var(--border); position: sticky; top: 0;
  height: 100vh; overflow-y: auto; padding: 28px 20px;
}
.sidebar-title {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.08em;
  margin-bottom: 16px; padding-bottom: 10px;
  border-bottom: 2px solid var(--primary);
}
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar li { margin: 0; padding: 0; }
.sidebar a {
  display: block; padding: 5px 8px; color: var(--text-secondary);
  text-decoration: none; font-size: 13px; line-height: 1.5;
  border-radius: var(--radius); transition: all 0.15s;
}
.sidebar a:hover { background: var(--bg-alt); color: var(--primary); }
.sidebar ul ul a { padding-left: 18px; font-size: 12.5px; }
.sidebar ul ul ul a { padding-left: 30px; font-size: 12px; color: #718096; }
.main {
  flex: 1; background: var(--bg); padding: 48px 64px; max-width: 900px;
}
h1, h2, h3, h4, h5, h6 {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  font-weight: 700; color: var(--primary); line-height: 1.3;
  margin-top: 2.2em; margin-bottom: 0.7em;
}
h1 {
  font-size: 32px; font-weight: 800; margin-top: 0; margin-bottom: 0.3em;
  letter-spacing: -0.02em;
}
h2 {
  font-size: 22px; padding-bottom: 0.4em;
  border-bottom: 1px solid var(--border-strong); margin-top: 2.5em;
}
h3 { font-size: 17px; color: var(--primary-light); margin-top: 1.8em; }
h4 { font-size: 15px; color: var(--text-secondary); margin-top: 1.5em; }
p {
  margin-bottom: 1em; text-align: justify;
  word-break: normal; overflow-wrap: break-word;
}
.report-header {
  margin-bottom: 40px; padding-bottom: 24px;
  border-bottom: 3px solid var(--primary);
}
.report-meta {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 13px; color: var(--text-secondary); margin-top: 12px;
  display: flex; gap: 20px; flex-wrap: wrap;
}
.exec-summary {
  background: var(--bg-alt); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px 28px; margin: 24px 0 32px;
}
.exec-summary h2 { margin-top: 0; font-size: 18px; border-bottom: none; color: var(--primary); }
table {
  width: 100%; border-collapse: collapse; margin: 1.2em 0;
  font-size: 13.5px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  box-shadow: var(--shadow); border-radius: var(--radius); overflow: hidden;
}
th {
  background: var(--primary); color: #fff; font-weight: 600;
  text-align: left; padding: 10px 14px; font-size: 12.5px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
td { padding: 9px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:nth-child(even) { background: var(--bg-alt); }
tr:hover { background: #e6f0fa; }
blockquote {
  margin: 1.2em 0; padding: 14px 20px;
  border-left: 4px solid var(--primary); background: var(--bg-alt);
  color: var(--text-secondary); font-size: 14px;
  border-radius: 0 var(--radius) var(--radius) 0;
}
blockquote p:last-child { margin-bottom: 0; }
ul, ol { margin: 0.8em 0; padding-left: 1.6em; }
li { margin-bottom: 0.35em; }
li::marker { color: var(--primary-light); }
code {
  font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
  font-size: 12.5px; background: var(--bg-card); padding: 2px 6px;
  border-radius: 4px; color: var(--accent);
}
pre {
  background: #1a202c; color: #e2e8f0; padding: 16px 20px;
  border-radius: var(--radius); overflow-x: auto;
  margin: 1em 0; font-size: 13px; line-height: 1.6;
}
pre code { background: transparent; color: inherit; padding: 0; }
hr { border: none; height: 1px; background: var(--border-strong); margin: 2.5em 0; }
a {
  color: var(--primary-light); text-decoration: none;
  border-bottom: 1px solid transparent; transition: border-color 0.15s;
}
a:hover { border-bottom-color: var(--primary-light); }
strong { font-weight: 700; color: var(--primary); }
.opportunity-card {
  background: var(--bg-alt); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 24px; margin: 16px 0;
}
.opportunity-card h3 { margin-top: 0; color: var(--primary); }
@media (max-width: 1024px) {
  .sidebar { display: none; }
  .main { padding: 32px; max-width: 100%; }
}
@media (max-width: 640px) {
  .main { padding: 20px; }
  h1 { font-size: 24px; }
  h2 { font-size: 18px; }
  table { font-size: 12px; }
  th, td { padding: 6px 8px; }
}
@media print {
  .sidebar { display: none; }
  .main { max-width: 100%; padding: 0; }
  body { background: #fff; }
  h2 { page-break-after: avoid; }
  table { page-break-inside: avoid; }
}
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | {author}</title>
  <meta name="author" content="{author}">
  <style>{CSS}</style>
</head>
<body>
  <div class="layout">
    <nav class="sidebar">
      <div class="sidebar-title">目录</div>
      {toc_html}
    </nav>
    <main class="main">
      <div class="report-header">
        <h1>{title}</h1>
        <div class="report-meta">
          <span>作者：{author}</span>
          {f'<span>日期：{date}</span>' if date else ''}
          <span>工具：business-consult/research</span>
        </div>
      </div>
      {html_body}
    </main>
  </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "10-research-report.md"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    generate(input_file, output_file)
