"""Markdown report generator for code scanner."""

import os


def write_md_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.md")

    repo = result["repository"]
    complexity = result["analysis"]["complexity"]
    security = result["analysis"]["security"]
    smells = result["analysis"]["smells"]
    duplicates = result["analysis"].get("duplicates", {})
    unused_imports = result["analysis"].get("unusedImports", {})
    problem_files = result["analysis"].get("problemFiles", [])
    trend = result.get("trend")
    roadmap = result.get("roadmap", [])
    quality_ctx = result.get("qualityContext", {})

    lines = []
    lines.append(f"# Code Scan Report\n")
    lines.append(f"**Quality Score: {result['qualityScore']}/100 (Grade: {result['grade']})**\n")

    if quality_ctx:
        lines.append(f"_{quality_ctx.get('industryBenchmark', '')}. Your ratio: {quality_ctx.get('flaggedRatio', 0)}%._\n")

    if trend:
        delta = trend["scoreDelta"]
        arrow = "+" if delta >= 0 else ""
        lines.append(f"**Trend:** {arrow}{delta} points since last scan\n")

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
    lines.append(f"| Duplicate Code Groups | {duplicates.get('totalGroups', 0)} |")
    lines.append(f"| Unused Imports | {unused_imports.get('totalUnused', 0)} |")
    lines.append(f"")

    # Languages
    lines.append(f"## Languages\n")
    lines.append(f"| Language | Files | Lines |")
    lines.append(f"|----------|-------|-------|")
    sorted_langs = sorted(repo["languages"].items(), key=lambda x: x[1]["files"], reverse=True)
    for lang, data in sorted_langs:
        lines.append(f"| {lang} | {data['files']:,} | {data['lines']:,} |")
    lines.append(f"")

    # Top problem files
    if problem_files:
        lines.append(f"## Top Problem Files\n")
        lines.append(f"| File | Total Issues | Complexity | Security | Smells |")
        lines.append(f"|------|-------------|-----------|----------|--------|")
        for pf in problem_files:
            b = pf["breakdown"]
            lines.append(f"| `{pf['file']}` | {pf['totalIssues']} | {b['complexity']} | {b['security']} | {b['smells']} |")
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

    # Duplicate code
    if duplicates.get("totalGroups", 0) > 0:
        lines.append(f"## Duplicate Code\n")
        lines.append(f"**{duplicates['totalGroups']} duplicate groups** totaling {duplicates['totalDuplicateLines']:,} lines\n")
        lines.append(f"| # | Lines | Locations |")
        lines.append(f"|---|-------|-----------|")
        for i, group in enumerate(duplicates.get("groups", [])[:10], 1):
            locs = ", ".join(f"`{loc['file']}:{loc['startLine']}`" for loc in group["locations"][:3])
            lines.append(f"| {i} | {group['lineCount']} | {locs} |")
        lines.append(f"")

    # Unused imports
    if unused_imports.get("totalUnused", 0) > 0:
        lines.append(f"## Unused Imports\n")
        lines.append(f"**{unused_imports['totalUnused']} unused** across {unused_imports['totalFiles']} files\n")
        lines.append(f"| File | Unused Symbols |")
        lines.append(f"|------|---------------|")
        for entry in unused_imports.get("files", [])[:15]:
            symbols = ", ".join(f"`{imp['symbol']}`" for imp in entry["imports"])
            lines.append(f"| `{entry['file']}` | {symbols} |")
        lines.append(f"")

    # Trend
    if trend:
        lines.append(f"## Trend\n")
        lines.append(f"| Category | Previous | Current | Delta |")
        lines.append(f"|----------|----------|---------|-------|")
        for cat, detail in trend["details"].items():
            d = detail["delta"]
            sign = "+" if d >= 0 else ""
            lines.append(f"| {cat.title()} | {detail['previous']} | {detail['current']} | {sign}{d} |")
        lines.append(f"")

    # Roadmap
    if roadmap:
        lines.append(f"## Remediation Roadmap\n")
        for item in roadmap:
            gain = f"+{item['estimatedScoreGain']} pts" if item["estimatedScoreGain"] > 0 else "maintainability"
            lines.append(f"{item['priority']}. **[{item['effort']}]** {item['action']} — _{gain}_")
        lines.append(f"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown report: {output_path}")
