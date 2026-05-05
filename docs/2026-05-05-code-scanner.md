# Code Scanner CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that scans a TypeScript/JavaScript codebase, analyzes complexity/security/smells, and generates JSON + Markdown + HTML reports with a quality score.

**Architecture:** Single-file scanner (`scanner.py`) handles CLI, traversal, and all analysis via regex. Two separate files (`report_html.py`, `report_md.py`) generate human-readable reports from the scanner's data dict. No external dependencies — stdlib only.

**Tech Stack:** Python 3.10+, argparse, pathlib, re, json, uuid, datetime

---

## File Structure

```
scanner.py          — CLI entry point, file traversal, analysis (complexity, security, smells), quality scoring, JSON output
report_md.py        — takes scan result dict, writes Markdown report
report_html.py      — takes scan result dict, writes self-contained HTML report
.gitignore          — ignores scan-results/
CLAUDE.md           — ground rules
.claude/commands/scan-and-report.md — feedback loop command
```

---

### Task 1: Project Setup & .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create .gitignore**

```
scan-results/
__pycache__/
*.pyc
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore for scan results and pycache"
```

---

### Task 2: CLI Skeleton & File Traversal

**Files:**
- Create: `scanner.py`

- [ ] **Step 1: Write scanner.py with CLI and traversal**

```python
#!/usr/bin/env python3
"""Code scanner CLI — analyzes TypeScript/JavaScript codebases."""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

IGNORE_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".nx"}

DEEP_ANALYSIS_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

LANGUAGE_MAP = {
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".py": "Python",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Scan a codebase and generate quality reports.")
    parser.add_argument("directory", help="Path to the codebase to scan")
    parser.add_argument("--output-dir", default="./scan-results", help="Where to write reports (default: ./scan-results)")
    parser.add_argument("--format", choices=["json", "md", "html", "all"], default="all", help="Report format (default: all)")
    parser.add_argument("--ignore", action="append", default=[], help="Additional directory names to ignore (repeatable)")
    return parser.parse_args()


def should_ignore(path, ignore_dirs):
    parts = path.parts
    for part in parts:
        if part in ignore_dirs:
            return True
    return False


def detect_language(filepath):
    ext = filepath.suffix.lower()
    return LANGUAGE_MAP.get(ext, "Other")


def count_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except (OSError, PermissionError):
        return {"loc": 0, "comments": 0, "blanks": 0, "total": 0}

    total = len(lines)
    blanks = 0
    comments = 0
    in_block_comment = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blanks += 1
            continue
        if in_block_comment:
            comments += 1
            if "*/" in stripped:
                in_block_comment = False
            continue
        if stripped.startswith("//"):
            comments += 1
            continue
        if stripped.startswith("/*"):
            comments += 1
            if "*/" not in stripped:
                in_block_comment = True
            continue

    loc = total - blanks - comments
    return {"loc": loc, "comments": comments, "blanks": blanks, "total": total}


def traverse(directory, ignore_dirs):
    root = Path(directory).resolve()
    if not root.is_dir():
        print(f"Error: '{directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    files = []
    file_count = 0

    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue
        relative = filepath.relative_to(root)
        if should_ignore(relative, ignore_dirs):
            continue
        language = detect_language(filepath)
        metrics = count_lines(filepath)
        files.append({
            "path": str(relative).replace("\\", "/"),
            "language": language,
            "metrics": metrics,
            "absolute_path": str(filepath),
        })
        file_count += 1
        if file_count % 500 == 0:
            print(f"  Scanned {file_count} files...", file=sys.stderr)

    print(f"  Total: {file_count} files scanned.", file=sys.stderr)
    return files


def build_result(directory, files):
    languages = {}
    total_lines = 0

    for f in files:
        lang = f["language"]
        if lang not in languages:
            languages[lang] = {"files": 0, "lines": 0}
        languages[lang]["files"] += 1
        languages[lang]["lines"] += f["metrics"]["loc"]
        total_lines += f["metrics"]["loc"]

    return {
        "scanId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "path": str(Path(directory).resolve()),
            "totalFiles": len(files),
            "totalLines": total_lines,
            "languages": languages,
        },
        "files": files,
        "analysis": {
            "complexity": {"totalFunctions": 0, "flaggedFunctions": 0, "functions": []},
            "security": {"issues": [], "counts": {"high": 0, "medium": 0, "low": 0}},
            "smells": {"issues": [], "summary": {"long_functions": 0, "deep_nesting": 0, "long_params": 0, "large_files": 0}},
        },
        "qualityScore": 100,
        "grade": "A",
    }


def write_json_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.json")

    output = dict(result)
    output["files"] = sorted(result["files"], key=lambda f: f["metrics"]["loc"], reverse=True)[:100]
    for f in output["files"]:
        f.pop("absolute_path", None)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"  JSON report: {output_path}", file=sys.stderr)


def main():
    args = parse_args()
    ignore_dirs = IGNORE_DIRS | set(args.ignore)

    print(f"Scanning: {args.directory}", file=sys.stderr)
    files = traverse(args.directory, ignore_dirs)
    result = build_result(args.directory, files)

    fmt = args.format
    if fmt in ("json", "all"):
        write_json_report(result, args.output_dir)
    if fmt in ("md", "all"):
        from report_md import write_md_report
        write_md_report(result, args.output_dir)
    if fmt in ("html", "all"):
        from report_html import write_html_report
        write_html_report(result, args.output_dir)

    print(f"\n  Quality Score: {result['qualityScore']}/100 (Grade: {result['grade']})", file=sys.stderr)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create stub report files so imports don't break**

Create `report_md.py`:
```python
"""Markdown report generator."""

import os


def write_md_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Scan Report\n\n_TODO: implement_\n")
    print(f"  Markdown report: {output_path}")
```

Create `report_html.py`:
```python
"""HTML report generator."""

import os


def write_html_report(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Scan Report</h1><p>TODO: implement</p></body></html>\n")
    print(f"  HTML report: {output_path}")
```

- [ ] **Step 3: Test basic traversal**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format json`

Expected: Prints progress, writes `scan-results/report.json` with valid JSON containing file counts and language breakdown.

Verify: `python -c "import json; d=json.load(open('scan-results/report.json')); print(d['repository']['totalFiles'], 'files,', d['repository']['totalLines'], 'LOC')"`

- [ ] **Step 4: Commit**

```bash
git add scanner.py report_md.py report_html.py
git commit -m "feat: add CLI skeleton with file traversal and JSON output"
```

---

### Task 3: Cyclomatic Complexity Analysis

**Files:**
- Modify: `scanner.py` (add `analyze_complexity` function, call it from `main`)

- [ ] **Step 1: Add complexity analysis function to scanner.py**

Add after the `count_lines` function:

```python
import re

FUNCTION_PATTERNS = [
    re.compile(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\("),
    re.compile(r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\("),
    re.compile(r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?[^(]*=>\s*"),
    re.compile(r"^\s+(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w[^{]*)?\{", re.MULTILINE),
]

DECISION_PATTERN = re.compile(
    r"\b(?:if|else\s+if|while|for|case|catch)\b|&&|\|\||\?\?"
)


def analyze_complexity(files):
    functions = []

    for file_info in files:
        ext = Path(file_info["absolute_path"]).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue

        try:
            with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except (OSError, PermissionError):
            continue

        file_functions = find_functions(lines, file_info["path"])
        functions.extend(file_functions)

    flagged = [fn for fn in functions if fn["complexity"] > 10]
    flagged.sort(key=lambda fn: fn["complexity"], reverse=True)

    return {
        "totalFunctions": len(functions),
        "flaggedFunctions": len(flagged),
        "functions": flagged[:50],
    }


def find_functions(lines, filepath):
    functions = []
    i = 0
    while i < len(lines):
        line = lines[i]
        func_name = None

        for pattern in FUNCTION_PATTERNS:
            match = pattern.search(line)
            if match:
                func_name = match.group(1)
                break

        if func_name:
            func_start = i
            brace_count = 0
            started = False
            func_end = i

            for j in range(i, len(lines)):
                brace_count += lines[j].count("{") - lines[j].count("}")
                if not started and "{" in lines[j]:
                    started = True
                if started and brace_count <= 0:
                    func_end = j
                    break
            else:
                func_end = len(lines) - 1

            func_body = "\n".join(lines[func_start:func_end + 1])
            decisions = len(DECISION_PATTERN.findall(func_body))
            complexity = 1 + decisions

            functions.append({
                "file": filepath,
                "name": func_name,
                "line": func_start + 1,
                "complexity": complexity,
                "length": func_end - func_start + 1,
            })

            i = func_end + 1
        else:
            i += 1

    return functions
```

- [ ] **Step 2: Wire complexity into the main flow**

In `build_result`, after creating the result dict, add:

```python
def build_result(directory, files):
    # ... existing code building the result dict ...

    # Run analysis on deep-analysis files
    print("  Analyzing complexity...", file=sys.stderr)
    result["analysis"]["complexity"] = analyze_complexity(files)

    return result
```

- [ ] **Step 3: Test complexity analysis**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format json`

Verify: `python -c "import json; d=json.load(open('scan-results/report.json')); c=d['analysis']['complexity']; print(f\"{c['totalFunctions']} functions, {c['flaggedFunctions']} flagged (complexity > 10)\"); [print(f\"  {fn['name']} ({fn['file']}:{fn['line']}) = {fn['complexity']}\") for fn in c['functions'][:5]]"`

Expected: Non-zero function count, some flagged functions with complexity > 10.

- [ ] **Step 4: Commit**

```bash
git add scanner.py
git commit -m "feat: add cyclomatic complexity analysis for TS/JS"
```

---

### Task 4: Security Scanning

**Files:**
- Modify: `scanner.py` (add `analyze_security` function, call it from `build_result`)

- [ ] **Step 1: Add security analysis function to scanner.py**

Add after `find_functions`:

```python
SECRET_PATTERNS = [
    (re.compile(r"""(?:api[_-]?key|secret|token|password|passwd|apikey)\s*[:=]\s*['"][A-Za-z0-9+/=_\-]{8,}['"]""", re.IGNORECASE), "high", "hardcoded_secret", "Possible hardcoded secret assigned to sensitive variable"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "high", "aws_key", "AWS access key ID detected"),
    (re.compile(r"-----BEGIN.*PRIVATE KEY-----"), "high", "private_key", "Private key detected"),
    (re.compile(r"""\beval\s*\("""), "medium", "dangerous_function", "Use of eval()"),
    (re.compile(r"""\bnew\s+Function\s*\("""), "medium", "dangerous_function", "Use of Function constructor"),
    (re.compile(r"""\.innerHTML\s*="""), "medium", "dangerous_function", "Direct innerHTML assignment"),
    (re.compile(r"""dangerouslySetInnerHTML"""), "medium", "dangerous_function", "Use of dangerouslySetInnerHTML"),
    (re.compile(r"""['"]http://(?!localhost)"""), "low", "non_https", "Non-HTTPS URL (excluding localhost)"),
    (re.compile(r"""eslint-disable.*security""", re.IGNORECASE), "low", "disabled_lint", "Security lint rule disabled"),
]


def analyze_security(files):
    issues = []
    counts = {"high": 0, "medium": 0, "low": 0}

    for file_info in files:
        ext = Path(file_info["absolute_path"]).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue

        try:
            with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except (OSError, PermissionError):
            continue

        for line_num, line in enumerate(lines, 1):
            for pattern, severity, category, description in SECRET_PATTERNS:
                if pattern.search(line):
                    issues.append({
                        "file": file_info["path"],
                        "line": line_num,
                        "severity": severity,
                        "category": category,
                        "description": description,
                    })
                    counts[severity] += 1
                    break

    issues.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
    return {"issues": issues[:100], "counts": counts}
```

- [ ] **Step 2: Wire security into build_result**

Add to `build_result` after the complexity call:

```python
    print("  Scanning for security issues...", file=sys.stderr)
    result["analysis"]["security"] = analyze_security(files)
```

- [ ] **Step 3: Test security scanning**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format json`

Verify: `python -c "import json; d=json.load(open('scan-results/report.json')); s=d['analysis']['security']; print(f\"Security issues: {s['counts']}\"); [print(f\"  [{i['severity']}] {i['file']}:{i['line']} - {i['description']}\") for i in s['issues'][:5]]"`

Expected: Some security findings (likely hardcoded tokens or innerHTML in a real project).

- [ ] **Step 4: Commit**

```bash
git add scanner.py
git commit -m "feat: add security scanning with pattern detection"
```

---

### Task 5: Code Smell Detection

**Files:**
- Modify: `scanner.py` (add `analyze_smells` function, call it from `build_result`)

- [ ] **Step 1: Add code smell detection to scanner.py**

Add after `analyze_security`:

```python
def analyze_smells(files):
    issues = []
    summary = {"long_functions": 0, "deep_nesting": 0, "long_params": 0, "large_files": 0}

    for file_info in files:
        ext = Path(file_info["absolute_path"]).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue

        if file_info["metrics"]["loc"] > 300:
            issues.append({
                "file": file_info["path"],
                "line": 1,
                "type": "large_file",
                "severity": "low",
                "details": f"File has {file_info['metrics']['loc']} lines of code",
            })
            summary["large_files"] += 1

        try:
            with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except (OSError, PermissionError):
            continue

        check_deep_nesting(lines, file_info["path"], issues, summary)
        check_long_params(lines, file_info["path"], issues, summary)

    smells_from_complexity = check_long_functions_from_complexity(files)
    issues.extend(smells_from_complexity)
    summary["long_functions"] = len(smells_from_complexity)

    issues.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
    return {"issues": issues[:100], "summary": summary}


def check_deep_nesting(lines, filepath, issues, summary):
    max_depth = 0
    current_depth = 0
    max_depth_line = 0

    for i, line in enumerate(lines, 1):
        current_depth += line.count("{") - line.count("}")
        if current_depth > max_depth:
            max_depth = current_depth
            max_depth_line = i

    if max_depth > 4:
        issues.append({
            "file": filepath,
            "line": max_depth_line,
            "type": "deep_nesting",
            "severity": "high",
            "details": f"Nesting depth reaches {max_depth} levels",
        })
        summary["deep_nesting"] += 1


def check_long_params(lines, filepath, issues, summary):
    param_pattern = re.compile(r"(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?)\s*\(([^)]{50,})\)")
    for i, line in enumerate(lines, 1):
        match = param_pattern.search(line)
        if match:
            params = match.group(1).split(",")
            if len(params) > 5:
                issues.append({
                    "file": filepath,
                    "line": i,
                    "type": "long_params",
                    "severity": "medium",
                    "details": f"Function has {len(params)} parameters",
                })
                summary["long_params"] += 1


def check_long_functions_from_complexity(files):
    issues = []
    for file_info in files:
        ext = Path(file_info["absolute_path"]).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue

        try:
            with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().split("\n")
        except (OSError, PermissionError):
            continue

        funcs = find_functions(lines, file_info["path"])
        for fn in funcs:
            if fn["length"] > 50:
                issues.append({
                    "file": fn["file"],
                    "line": fn["line"],
                    "type": "long_function",
                    "severity": "medium",
                    "details": f"Function '{fn['name']}' is {fn['length']} lines",
                })
    return issues
```

- [ ] **Step 2: Wire smells into build_result**

Add to `build_result` after security:

```python
    print("  Detecting code smells...", file=sys.stderr)
    result["analysis"]["smells"] = analyze_smells(files)
```

- [ ] **Step 3: Test code smell detection**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format json`

Verify: `python -c "import json; d=json.load(open('scan-results/report.json')); s=d['analysis']['smells']; print(f\"Smells: {s['summary']}\"); [print(f\"  [{i['type']}] {i['file']}:{i['line']} - {i['details']}\") for i in s['issues'][:5]]"`

Expected: Some large files and long functions detected in a 14k-file codebase.

- [ ] **Step 4: Commit**

```bash
git add scanner.py
git commit -m "feat: add code smell detection (nesting, params, file size, function length)"
```

---

### Task 6: Quality Scoring

**Files:**
- Modify: `scanner.py` (add `calculate_quality_score` function, call it from `build_result`)

- [ ] **Step 1: Add quality score calculation to scanner.py**

Add after `check_long_functions_from_complexity`:

```python
def calculate_quality_score(result):
    complexity = result["analysis"]["complexity"]
    security = result["analysis"]["security"]
    smells = result["analysis"]["smells"]
    total_files = result["repository"]["totalFiles"]

    # Complexity factor (40%): penalize ratio of flagged functions
    total_funcs = complexity["totalFunctions"]
    if total_funcs > 0:
        flagged_ratio = complexity["flaggedFunctions"] / total_funcs
        complexity_score = max(0, 100 - (flagged_ratio * 500))
    else:
        complexity_score = 100

    # Security factor (30%): penalize by severity
    security_penalty = (
        security["counts"]["high"] * 10
        + security["counts"]["medium"] * 5
        + security["counts"]["low"] * 2
    )
    security_score = max(0, 100 - min(security_penalty, 100))

    # Smells factor (30%): penalize ratio of smells to files
    total_smells = sum(smells["summary"].values())
    if total_files > 0:
        smell_ratio = total_smells / total_files
        smells_score = max(0, 100 - (smell_ratio * 200))
    else:
        smells_score = 100

    weighted = (
        complexity_score * 0.4
        + security_score * 0.3
        + smells_score * 0.3
    )
    score = round(weighted)

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    return score, grade
```

- [ ] **Step 2: Wire scoring into build_result**

Add to `build_result` after smells analysis:

```python
    score, grade = calculate_quality_score(result)
    result["qualityScore"] = score
    result["grade"] = grade
```

- [ ] **Step 3: Test quality scoring**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format json`

Verify: `python -c "import json; d=json.load(open('scan-results/report.json')); print(f\"Quality: {d['qualityScore']}/100 — Grade: {d['grade']}\")"` 

Expected: A numeric score between 0-100 and a letter grade.

- [ ] **Step 4: Commit**

```bash
git add scanner.py
git commit -m "feat: add quality scoring system (0-100, letter grades)"
```

---

### Task 7: Markdown Report Generator

**Files:**
- Modify: `report_md.py` (replace stub with full implementation)

- [ ] **Step 1: Implement full Markdown report**

Replace `report_md.py` contents:

```python
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
```

- [ ] **Step 2: Test Markdown report**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format md`

Verify: `head -30 scan-results/report.md`

Expected: A well-formatted Markdown file with tables showing summary, languages, and analysis results.

- [ ] **Step 3: Commit**

```bash
git add report_md.py
git commit -m "feat: implement full Markdown report generator"
```

---

### Task 8: HTML Report Generator

**Files:**
- Modify: `report_html.py` (replace stub with full implementation)

- [ ] **Step 1: Implement full HTML report**

Replace `report_html.py` contents:

```python
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
```

- [ ] **Step 2: Test HTML report**

Run: `python scanner.py C:\Projects\mdc-excel-addin --format html`

Verify: Open `scan-results/report.html` in a browser. Confirm:
- Score and grade display prominently
- Language bar chart renders
- All tables populated
- No console errors

- [ ] **Step 3: Commit**

```bash
git add report_html.py
git commit -m "feat: implement self-contained HTML report with charts"
```

---

### Task 9: Full Integration Test

**Files:**
- No new files — validation only

- [ ] **Step 1: Run full scan with all formats**

Run: `python scanner.py C:\Projects\mdc-excel-addin`

Expected output:
```
Scanning: C:\Projects\mdc-excel-addin
  Scanned 500 files...
  Scanned 1000 files...
  ...
  Total: ~15000 files scanned.
  Analyzing complexity...
  Scanning for security issues...
  Detecting code smells...
  JSON report: ./scan-results/report.json
  Markdown report: ./scan-results/report.md
  HTML report: ./scan-results/report.html

  Quality Score: XX/100 (Grade: X)
```

- [ ] **Step 2: Validate JSON**

Run: `python -c "import json; d=json.load(open('scan-results/report.json')); print(json.dumps({k:v for k,v in d.items() if k != 'files'}, indent=2))"`

Expected: Valid JSON with all fields populated, no null values.

- [ ] **Step 3: Validate Markdown**

Run: `cat scan-results/report.md | head -50`

Expected: Well-formatted Markdown tables.

- [ ] **Step 4: Validate HTML**

Open `scan-results/report.html` in browser. Check all sections render correctly.

- [ ] **Step 5: Fix any issues found, re-run**

If any output is broken, fix the source and re-run. Repeat until clean.

---

### Task 10: Infrastructure — CLAUDE.md & Custom Command

**Files:**
- Create: `CLAUDE.md`
- Create: `.claude/commands/scan-and-report.md`

- [ ] **Step 1: Create CLAUDE.md**

```markdown
# Ground Rules

- Run `python scanner.py C:\Projects\mdc-excel-addin` to test changes — verify JSON output is valid before committing
- TypeScript analysis is regex-based, not AST — don't attempt to parse type annotations for complexity
- HTML report must be fully self-contained — no CDN dependencies, no external files
- Keep scanner.py under 400 lines — if it grows larger, the analysis functions need refactoring into helpers
- Always test with --format json first (fastest), then validate other formats
```

- [ ] **Step 2: Create custom command**

Create `.claude/commands/scan-and-report.md`:

```markdown
Run the code scanner and validate all outputs:

1. Run: `python scanner.py C:\Projects\mdc-excel-addin`
2. Validate JSON: `python -c "import json; d=json.load(open('scan-results/report.json')); print(f\"Score: {d['qualityScore']}/100 ({d['grade']})\")"` 
3. Check HTML report exists and is non-empty: `test -s scan-results/report.html && echo "HTML OK" || echo "HTML MISSING"`
4. Check Markdown report exists and is non-empty: `test -s scan-results/report.md && echo "MD OK" || echo "MD MISSING"`
5. Report the quality score and grade
6. If any step fails, diagnose and fix the issue, then re-run from step 1
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md .claude/commands/scan-and-report.md
git commit -m "feat: add ground rules and scan-and-report custom command"
```

---

### Task 11: Final Validation & Cleanup

**Files:**
- No new files

- [ ] **Step 1: Run the custom command workflow**

Execute the full scan-and-report workflow manually to confirm it works end-to-end.

- [ ] **Step 2: Verify Definition of Done**

Check off:
- [ ] Functional scanner (walks codebase, extracts metrics)
- [ ] 3 analysis features working (complexity, security, smells)
- [ ] JSON + Markdown + HTML report formats
- [ ] Quality scoring (0-100, letter grade)
- [ ] CLAUDE.md with ground rules
- [ ] Custom command encoding a workflow
- [ ] Feedback loop applied (scan → inspect → fix → rescan)

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup and validation"
```
