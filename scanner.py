#!/usr/bin/env python3
"""Code scanner CLI — analyzes TypeScript/JavaScript codebases."""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from analyzers import (
    analyze_complexity,
    analyze_security,
    analyze_smells,
    calculate_quality_score,
    find_functions,
)

IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__", ".nx",
    ".vite", ".next", ".webpack", ".mf-types", "cdk.out", "coverage", ".nyc_output",
    "nanofrontendTestBundle",
}

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
    parser.add_argument("--complexity-threshold", type=int, default=10, help="Cyclomatic complexity threshold (default: 10)")
    parser.add_argument("--large-file-threshold", type=int, default=300, help="LOC threshold for large files (default: 300)")
    parser.add_argument("--long-function-threshold", type=int, default=50, help="Line threshold for long functions (default: 50)")
    parser.add_argument("--no-history", action="store_true", default=False, help="Skip historical trend comparison")
    parser.add_argument("--no-duplicates", action="store_true", default=False, help="Skip duplicate code detection")
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


def compute_problem_files(result):
    file_issues = {}
    for fn in result["analysis"]["complexity"]["functions"]:
        f = fn["file"]
        file_issues.setdefault(f, {"file": f, "totalIssues": 0, "breakdown": {"complexity": 0, "security": 0, "smells": 0}})
        file_issues[f]["totalIssues"] += 1
        file_issues[f]["breakdown"]["complexity"] += 1
    for issue in result["analysis"]["security"]["issues"]:
        f = issue["file"]
        file_issues.setdefault(f, {"file": f, "totalIssues": 0, "breakdown": {"complexity": 0, "security": 0, "smells": 0}})
        file_issues[f]["totalIssues"] += 1
        file_issues[f]["breakdown"]["security"] += 1
    for issue in result["analysis"]["smells"]["issues"]:
        f = issue["file"]
        file_issues.setdefault(f, {"file": f, "totalIssues": 0, "breakdown": {"complexity": 0, "security": 0, "smells": 0}})
        file_issues[f]["totalIssues"] += 1
        file_issues[f]["breakdown"]["smells"] += 1
    ranked = sorted(file_issues.values(), key=lambda x: x["totalIssues"], reverse=True)
    return ranked[:10]


def compute_quality_context(result):
    complexity = result["analysis"]["complexity"]
    total_funcs = complexity["totalFunctions"]
    if total_funcs > 0:
        ratio = round(complexity["flaggedFunctions"] / total_funcs * 100, 1)
    else:
        ratio = 0.0
    if ratio <= 3:
        assessment = "excellent"
    elif ratio <= 8:
        assessment = "at_benchmark"
    else:
        assessment = "above_average"
    return {
        "flaggedRatio": ratio,
        "industryBenchmark": "Typical well-maintained codebases have 3-8% of functions exceeding complexity threshold of 10",
        "assessment": assessment,
    }


def build_result(directory, files, thresholds, output_dir, skip_history=False, skip_duplicates=False):
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
            "duplicates": {"totalGroups": 0, "totalDuplicateLines": 0, "groups": []},
            "unusedImports": {"totalFiles": 0, "totalUnused": 0, "files": []},
            "problemFiles": [],
        },
        "qualityScore": 100,
        "grade": "A",
        "qualityContext": {},
        "trend": None,
        "roadmap": [],
    }

    print("  Analyzing complexity...", file=sys.stderr)
    result["analysis"]["complexity"] = analyze_complexity(files, thresholds["complexity"])

    print("  Scanning for security issues...", file=sys.stderr)
    result["analysis"]["security"] = analyze_security(files)

    print("  Detecting code smells...", file=sys.stderr)
    result["analysis"]["smells"] = analyze_smells(files, thresholds)

    if not skip_duplicates:
        from detection import detect_duplicates
        print("  Detecting duplicate code...", file=sys.stderr)
        result["analysis"]["duplicates"] = detect_duplicates(files)

    from detection import detect_unused_imports
    print("  Detecting unused imports...", file=sys.stderr)
    result["analysis"]["unusedImports"] = detect_unused_imports(files)

    result["analysis"]["problemFiles"] = compute_problem_files(result)

    score, grade = calculate_quality_score(result)
    result["qualityScore"] = score
    result["grade"] = grade
    result["qualityContext"] = compute_quality_context(result)

    if not skip_history:
        from trends import compare_to_history, save_to_history
        print("  Comparing to history...", file=sys.stderr)
        result["trend"] = compare_to_history(result, output_dir)
        save_to_history(result, output_dir)

    from roadmap import generate_roadmap
    result["roadmap"] = generate_roadmap(result)

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
    thresholds = {
        "complexity": args.complexity_threshold,
        "large_file": args.large_file_threshold,
        "long_function": args.long_function_threshold,
    }

    print(f"Scanning: {args.directory}", file=sys.stderr)
    files = traverse(args.directory, ignore_dirs)
    result = build_result(
        args.directory, files, thresholds, args.output_dir,
        skip_history=args.no_history, skip_duplicates=args.no_duplicates,
    )

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
