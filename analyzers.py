"""Analysis functions for code scanner — complexity, security, smells, scoring."""

import re
from pathlib import Path

DEEP_ANALYSIS_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

TEST_FILE_SUFFIXES = (".test.ts", ".spec.ts", ".test.tsx", ".spec.tsx")

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
    (re.compile(r"""(?:api[_-]?key|secret|token|password|passwd|apikey)\s*[:=]\s*['"][A-Za-z0-9+/=_\-]{16,}['"]""", re.IGNORECASE), "high", "hardcoded_secret", "Possible hardcoded secret assigned to sensitive variable"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "high", "aws_key", "AWS access key ID detected"),
    (re.compile(r"-----BEGIN.*PRIVATE KEY-----"), "high", "private_key", "Private key detected"),
    (re.compile(r"""\beval\s*\("""), "medium", "dangerous_function", "Use of eval()"),
    (re.compile(r"""\bnew\s+Function\s*\("""), "medium", "dangerous_function", "Use of Function constructor"),
    (re.compile(r"""\.innerHTML\s*="""), "medium", "dangerous_function", "Direct innerHTML assignment"),
    (re.compile(r"""dangerouslySetInnerHTML"""), "medium", "dangerous_function", "Use of dangerouslySetInnerHTML"),
    (re.compile(r"""['"]http://(?!localhost)"""), "low", "non_https", "Non-HTTPS URL (excluding localhost)"),
    (re.compile(r"""eslint-disable.*security""", re.IGNORECASE), "low", "disabled_lint", "Security lint rule disabled"),
]


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


def _is_minified(content, lines):
    if not lines:
        return False
    avg_len = len(content) / len(lines)
    return avg_len > 150


def analyze_complexity(files, threshold=10):
    functions = []

    for file_info in files:
        filepath = file_info["absolute_path"]
        ext = Path(filepath).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue
        if filepath.endswith(".d.ts"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except (OSError, PermissionError):
            continue

        if _is_minified(content, lines):
            continue

        file_functions = find_functions(lines, file_info["path"])
        functions.extend(file_functions)

    flagged = [fn for fn in functions if fn["complexity"] > threshold]
    flagged.sort(key=lambda fn: fn["complexity"], reverse=True)

    return {
        "totalFunctions": len(functions),
        "flaggedFunctions": len(flagged),
        "functions": flagged[:50],
    }


def analyze_security(files, skip_test_files=True):
    issues = []
    counts = {"high": 0, "medium": 0, "low": 0}

    for file_info in files:
        filepath = file_info["absolute_path"]
        ext = Path(filepath).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue
        if skip_test_files and any(filepath.endswith(s) for s in TEST_FILE_SUFFIXES):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
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


def analyze_smells(files, thresholds=None):
    if thresholds is None:
        thresholds = {"large_file": 300, "long_function": 50}

    issues = []
    summary = {"long_functions": 0, "deep_nesting": 0, "long_params": 0, "large_files": 0}

    for file_info in files:
        filepath = file_info["absolute_path"]
        ext = Path(filepath).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue
        if filepath.endswith(".d.ts"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except (OSError, PermissionError):
            continue

        if _is_minified(content, lines):
            continue

        if file_info["metrics"]["loc"] > thresholds["large_file"]:
            issues.append({
                "file": file_info["path"],
                "line": 1,
                "type": "large_file",
                "severity": "low",
                "details": f"File has {file_info['metrics']['loc']} lines of code",
            })
            summary["large_files"] += 1

        lines_with_newline = [l + "\n" for l in lines]
        check_deep_nesting(lines_with_newline, file_info["path"], issues, summary)
        check_long_params(lines_with_newline, file_info["path"], issues, summary)

    smells_from_complexity = check_long_functions_from_complexity(files, thresholds["long_function"])
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


def check_long_functions_from_complexity(files, threshold=50):
    issues = []
    for file_info in files:
        filepath = file_info["absolute_path"]
        ext = Path(filepath).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue
        if filepath.endswith(".d.ts"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except (OSError, PermissionError):
            continue

        if _is_minified(content, lines):
            continue

        funcs = find_functions(lines, file_info["path"])
        for fn in funcs:
            if fn["length"] > threshold:
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

    total_funcs = complexity["totalFunctions"]
    if total_funcs > 0:
        flagged_ratio = complexity["flaggedFunctions"] / total_funcs
        complexity_score = max(0, 100 - (flagged_ratio * 500))
    else:
        complexity_score = 100

    security_penalty = (
        security["counts"]["high"] * 10
        + security["counts"]["medium"] * 5
        + security["counts"]["low"] * 2
    )
    security_score = max(0, 100 - min(security_penalty, 100))

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
