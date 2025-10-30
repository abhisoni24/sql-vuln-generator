import html
from typing import List, Dict


def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_markdown_file(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def append_to_markdown_file(file_path: str, content: str) -> None:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)


def escape_cell(s: str) -> str:
    if s is None:
        return ""
    return html.escape(str(s)).replace("|", "&#124;").replace("\n", "<br>")


def write_markdown_results(path: str, results: List[Dict]) -> None:
    header = "| original prompt | returned sql code | verdict | ground_truth |\n"
    header += "|---|---|---|---|\n"
    rows = []
    for r in results:
        p = escape_cell((r.get("original_prompt") or r.get("prompt") or ""))
        sql = escape_cell((r.get("sql_code") or r.get("sql") or ""))
        verdict = escape_cell((r.get("verdict") or ""))
        gt = escape_cell((r.get("ground_truth") or "unknown"))
        rows.append(f"| {p} | {sql} | {verdict} | {gt} |")
    body = "\n".join(rows)
    md = "# Results\n\n" + header + body + "\n\n"
    md += "## Full analysis\n\n"
    for i, r in enumerate(results, 1):
        md += f"### {i}. Prompt\n\n{r.get('original_prompt')}\n\n"
        md += "```sql\n" + (r.get('sql_code') or r.get('sql') or "") + "\n```\n\n"
        md += "**Verdict:** " + (r.get('verdict') or "") + "\n\n"
        md += "**Analysis:**\n\n" + (r.get('analysis') or "") + "\n\n"
        md += "---\n\n"

    write_markdown_file(path, md)