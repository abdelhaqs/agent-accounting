"""Report & Dashboard Compiler.

Inspired by Quarto / HTML report generation in modern data engineering templates.
Converts markdown audit reports in docs/comparisons_and_value_checks/ into
standalone, styled, self-contained interactive HTML dashboards.
"""
from __future__ import annotations

import re
from pathlib import Path


def convert_markdown_to_html(md_text: str, title: str = "Agent Accounting Audit Report") -> str:
    # Basic markdown transforms
    html_lines = []
    in_table = False
    in_code = False

    for line in md_text.splitlines():
        if line.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # Headers
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:]}</h4>")
        elif line.startswith("|") and line.endswith("|"):
            if "---" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "th" if not in_table else "td"
            row_html = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            # Style status badges
            row_html = re.sub(
                r"<td>(\*\*OK\*\*|OK)</td>",
                r'<td><span class="badge badge-ok">OK</span></td>',
                row_html,
            )
            row_html = re.sub(
                r"<td>(\*\*MISMATCH\*\*|MISMATCH)</td>",
                r'<td><span class="badge badge-fail">MISMATCH</span></td>',
                row_html,
            )
            if not in_table:
                html_lines.append("<table><thead><tr>" + row_html + "</tr></thead><tbody>")
                in_table = True
            else:
                html_lines.append("<tr>" + row_html + "</tr>")
        else:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            if line.strip():
                # Formats
                formatted = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
                formatted = re.sub(r"`(.*?)`", r"<code>\1</code>", formatted)
                html_lines.append(f"<p>{formatted}</p>")

    if in_table:
        html_lines.append("</tbody></table>")

    body_content = "\n".join(html_lines)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --muted: #94a3b8;
            --primary: #38bdf8;
            --success: #22c55e;
            --danger: #ef4444;
            --card-bg: rgba(30, 41, 59, 0.7);
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        h1, h2, h3, h4 {{
            color: var(--primary);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.4rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #0f172a;
            color: var(--primary);
            font-weight: 600;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}
        code {{
            background: #090d16;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
            color: #e2e8f0;
            font-size: 0.9em;
        }}
        pre {{
            background: #090d16;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            overflow-x: auto;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .badge-ok {{
            background: rgba(34, 197, 94, 0.2);
            color: var(--success);
            border: 1px solid var(--success);
        }}
        .badge-fail {{
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
            border: 1px solid var(--danger);
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_content}
    </div>
</body>
</html>
"""


def main():
    docs_dir = Path(__file__).resolve().parent / "docs" / "comparisons_and_value_checks"
    reports = sorted(docs_dir.glob("all_agents_uniblock_rpc_report_*.md"), reverse=True)
    if not reports:
        reports = sorted(docs_dir.glob("*.md"), reverse=True)

    if not reports:
        print("No reports found in docs/comparisons_and_value_checks/")
        return

    latest_report = reports[0]
    print(f"Reading latest report: {latest_report.name}")
    md_content = latest_report.read_text(encoding="utf-8")
    html_output = convert_markdown_to_html(md_content, title=f"Agent Accounting — {latest_report.stem}")

    dest_file = docs_dir / "latest_audit_dashboard.html"
    dest_file.write_text(html_output, encoding="utf-8")
    print(f"Compiled standalone dashboard: {dest_file.resolve()}")


if __name__ == "__main__":
    main()
