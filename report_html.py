"""HTML report generator for code scanner — self-contained single file."""

import os
import json


def write_html_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.html")

    repo = result["repository"]
    complexity = result["analysis"]["complexity"]
    security = result["analysis"]["security"]
    smells = result["analysis"]["smells"]
    score = result["qualityScore"]
    grade = result["grade"]

    grade_color = {"A": "#2d7a3a", "B": "#4a7a2d", "C": "#7a6b2d", "D": "#7a4a2d", "F": "#9a3a2d"}.get(grade, "#333")

    # Language chart data
    sorted_langs = sorted(repo["languages"].items(), key=lambda x: x[1]["files"], reverse=True)[:8]
    lang_labels = json.dumps([l[0] for l in sorted_langs])
    lang_files = json.dumps([l[1]["files"] for l in sorted_langs])
    lang_lines = json.dumps([l[1]["lines"] for l in sorted_langs])

    # Complexity data for top functions
    top_funcs = complexity["functions"][:10]
    func_rows = ""
    for fn in top_funcs:
        func_rows += f"<tr><td><code>{fn['name']}</code></td><td><code>{fn['file']}</code></td><td>{fn['line']}</td><td class=\"{'high' if fn['complexity']>15 else 'mid'}\">{fn['complexity']}</td></tr>\n"

    # Security rows
    sec_rows = ""
    for issue in security["issues"][:20]:
        sev_class = issue["severity"]
        sec_rows += f"<tr><td class=\"{sev_class}\">{issue['severity'].upper()}</td><td><code>{issue['file']}</code></td><td>{issue['line']}</td><td>{issue['description']}</td></tr>\n"

    # Smell rows
    smell_rows = ""
    for smell in smells["issues"][:15]:
        smell_rows += f"<tr><td>{smell['type']}</td><td><code>{smell['file']}</code></td><td>{smell['line']}</td><td>{smell['details']}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Scan Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #333; padding: 24px; }}
        .header {{ text-align: center; margin-bottom: 32px; }}
        .header h1 {{ color: #1a1a2e; margin-bottom: 8px; }}
        .score {{ font-size: 72px; font-weight: 700; color: {grade_color}; }}
        .grade {{ font-size: 36px; font-weight: 600; color: {grade_color}; margin-left: 12px; }}
        .subtitle {{ color: #666; margin-top: 8px; }}
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .stat-card {{ background: #fff; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-card .value {{ font-size: 28px; font-weight: 700; color: #1a1a2e; }}
        .stat-card .label {{ font-size: 13px; color: #666; margin-top: 4px; }}
        .section {{ background: #fff; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #1a1a2e; margin-bottom: 16px; font-size: 18px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: #1a1a2e; color: #fff; padding: 10px 8px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f8fa; }}
        .high {{ color: #9a3a2d; font-weight: 600; }}
        .medium {{ color: #7a6b2d; font-weight: 600; }}
        .low {{ color: #4a7a2d; font-weight: 600; }}
        .mid {{ color: #7a6b2d; font-weight: 600; }}
        .bar-chart {{ margin-top: 12px; }}
        .bar-row {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .bar-label {{ width: 100px; font-size: 13px; color: #555; flex-shrink: 0; }}
        .bar-track {{ flex: 1; background: #eee; border-radius: 4px; height: 24px; position: relative; }}
        .bar-fill {{ height: 100%; border-radius: 4px; background: #1a1a2e; display: flex; align-items: center; padding-left: 8px; font-size: 11px; color: #fff; font-weight: 600; min-width: 24px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Scan Report</h1>
        <div><span class="score">{score}</span><span class="grade">{grade}</span></div>
        <p class="subtitle">{repo['path']}</p>
    </div>

    <div class="dashboard">
        <div class="stat-card"><div class="value">{repo['totalFiles']:,}</div><div class="label">Files</div></div>
        <div class="stat-card"><div class="value">{repo['totalLines']:,}</div><div class="label">Lines of Code</div></div>
        <div class="stat-card"><div class="value">{complexity['totalFunctions']:,}</div><div class="label">Functions</div></div>
        <div class="stat-card"><div class="value">{complexity['flaggedFunctions']}</div><div class="label">Complex (>10)</div></div>
        <div class="stat-card"><div class="value">{sum(security['counts'].values())}</div><div class="label">Security Issues</div></div>
        <div class="stat-card"><div class="value">{sum(smells['summary'].values())}</div><div class="label">Code Smells</div></div>
    </div>

    <div class="section">
        <h2>Language Distribution</h2>
        <div class="bar-chart" id="lang-chart"></div>
    </div>

    <div class="section">
        <h2>Top Complex Functions</h2>
        <table>
            <thead><tr><th>Function</th><th>File</th><th>Line</th><th>Complexity</th></tr></thead>
            <tbody>{func_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>Security Issues</h2>
        <p style="margin-bottom:12px;color:#666;">High: {security['counts']['high']} | Medium: {security['counts']['medium']} | Low: {security['counts']['low']}</p>
        <table>
            <thead><tr><th>Severity</th><th>File</th><th>Line</th><th>Description</th></tr></thead>
            <tbody>{sec_rows}</tbody>
        </table>
    </div>

    <div class="section">
        <h2>Code Smells</h2>
        <div class="dashboard" style="margin-bottom:16px;">
            <div class="stat-card"><div class="value">{smells['summary']['long_functions']}</div><div class="label">Long Functions</div></div>
            <div class="stat-card"><div class="value">{smells['summary']['deep_nesting']}</div><div class="label">Deep Nesting</div></div>
            <div class="stat-card"><div class="value">{smells['summary']['long_params']}</div><div class="label">Long Params</div></div>
            <div class="stat-card"><div class="value">{smells['summary']['large_files']}</div><div class="label">Large Files</div></div>
        </div>
        <table>
            <thead><tr><th>Type</th><th>File</th><th>Line</th><th>Details</th></tr></thead>
            <tbody>{smell_rows}</tbody>
        </table>
    </div>

    <script>
    const langLabels = {lang_labels};
    const langFiles = {lang_files};
    const langLines = {lang_lines};
    const maxFiles = Math.max(...langFiles);

    const chartEl = document.getElementById('lang-chart');
    chartEl.innerHTML = langLabels.map((label, i) => {{
        const pct = (langFiles[i] / maxFiles) * 100;
        return `<div class="bar-row">
            <span class="bar-label">${{label}}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width:${{pct}}%">${{langFiles[i].toLocaleString()}} files</div>
            </div>
        </div>`;
    }}).join('');
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  HTML report: {output_path}")
