"""Markdown report generator for code scanner."""

import os


def write_md_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.md")

    repo = result["repository"]
    complexity = result["analysis"]["complexity"]
    security = result["analysis"]["security"]
    smells = result["analysis"]["smells"]

    lines = []
    lines.append(f"# Code Scan Report\n")
    lines.append(f"**Quality Score: {result['qualityScore']}/100 (Grade: {result['grade']})**\n")
    lines.append(f"---\n")

    # Summary
    lines.append(f"## Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Path | `{repo['path']}` |")
    lines.append(f"| Total Files | {repo['totalFiles']:,} |")
    lines.append(f"| Total Lines of Code | {repo['totalLines']:,} |")
    lines.append(f"| Functions Analyzed | {complexity['totalFunctions']:,} |")
    lines.append(f"| Complex Functions (>10) | {complexity['flaggedFunctions']} |")
    lines.append(f"| Security Issues | {sum(security['counts'].values())} |")
    lines.append(f"| Code Smells | {sum(smells['summary'].values())} |")
    lines.append(f"")

    # Languages
    lines.append(f"## Languages\n")
    lines.append(f"| Language | Files | Lines |")
    lines.append(f"|----------|-------|-------|")
    sorted_langs = sorted(repo["languages"].items(), key=lambda x: x[1]["files"], reverse=True)
    for lang, data in sorted_langs:
        lines.append(f"| {lang} | {data['files']:,} | {data['lines']:,} |")
    lines.append(f"")

    # Top complex functions
    if complexity["functions"]:
        lines.append(f"## Top Complex Functions\n")
        lines.append(f"| Function | File | Line | Complexity |")
        lines.append(f"|----------|------|------|-----------|")
        for fn in complexity["functions"][:10]:
            lines.append(f"| `{fn['name']}` | `{fn['file']}` | {fn['line']} | {fn['complexity']} |")
        lines.append(f"")

    # Security issues
    if security["issues"]:
        lines.append(f"## Security Issues\n")
        lines.append(f"**High:** {security['counts']['high']} | **Medium:** {security['counts']['medium']} | **Low:** {security['counts']['low']}\n")
        lines.append(f"| Severity | File | Line | Description |")
        lines.append(f"|----------|------|------|-------------|")
        for issue in security["issues"][:20]:
            sev = issue["severity"].upper()
            lines.append(f"| {sev} | `{issue['file']}` | {issue['line']} | {issue['description']} |")
        lines.append(f"")

    # Code smells
    if smells["issues"]:
        lines.append(f"## Code Smells\n")
        s = smells["summary"]
        lines.append(f"| Type | Count |")
        lines.append(f"|------|-------|")
        lines.append(f"| Long Functions (>50 lines) | {s['long_functions']} |")
        lines.append(f"| Deep Nesting (>4 levels) | {s['deep_nesting']} |")
        lines.append(f"| Long Parameter Lists (>5) | {s['long_params']} |")
        lines.append(f"| Large Files (>300 LOC) | {s['large_files']} |")
        lines.append(f"")
        lines.append(f"### Top Offenders\n")
        lines.append(f"| Type | File | Line | Details |")
        lines.append(f"|------|------|------|---------|")
        for smell in smells["issues"][:15]:
            lines.append(f"| {smell['type']} | `{smell['file']}` | {smell['line']} | {smell['details']} |")
        lines.append(f"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown report: {output_path}")
