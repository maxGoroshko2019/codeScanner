#!/usr/bin/env python3
"""Code scanner CLI — analyzes TypeScript/JavaScript codebases."""

import argparse
import json
import os
import re
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

FUNCTION_PATTERNS = [
    re.compile(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\("),
    re.compile(r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\("),
    re.compile(r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?[^(]*=>\s*"),
    re.compile(r"^\s+(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w[^{]*)?\{", re.MULTILINE),
]

DECISION_PATTERN = re.compile(
    r"\b(?:if|else\s+if|while|for|case|catch)\b|&&|\|\||\?\?"
)

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

    result = {
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

    print("  Analyzing complexity...", file=sys.stderr)
    result["analysis"]["complexity"] = analyze_complexity(files)

    print("  Scanning for security issues...", file=sys.stderr)
    result["analysis"]["security"] = analyze_security(files)

    print("  Detecting code smells...", file=sys.stderr)
    result["analysis"]["smells"] = analyze_smells(files)

    score, grade = calculate_quality_score(result)
    result["qualityScore"] = score
    result["grade"] = grade

    return result


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
