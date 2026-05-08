"""Duplicate code detection and unused imports analysis."""

import hashlib
import re
from pathlib import Path

DEEP_ANALYSIS_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

IMPORT_PATTERNS = [
    re.compile(r"""import\s+\{([^}]+)\}\s+from\s+['"]"""),
    re.compile(r"""import\s+(\w+)\s+from\s+['"]"""),
    re.compile(r"""import\s+\*\s+as\s+(\w+)\s+from\s+['"]"""),
]


def normalize_line(line):
    stripped = line.strip()
    comment_idx = stripped.find("//")
    if comment_idx > 0:
        stripped = stripped[:comment_idx].rstrip()
    return stripped


def detect_duplicates(files, window_size=5):
    hash_map = {}

    for file_info in files:
        filepath = file_info["absolute_path"]
        ext = Path(filepath).suffix.lower()
        if ext not in DEEP_ANALYSIS_EXTENSIONS:
            continue
        if filepath.endswith(".d.ts"):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw_lines = f.readlines()
        except (OSError, PermissionError):
            continue

        if len(raw_lines) < 10:
            continue

        total_len = sum(len(l) for l in raw_lines)
        if total_len / max(len(raw_lines), 1) > 150:
            continue

        normalized = []
        line_nums = []
        for i, line in enumerate(raw_lines, 1):
            n = normalize_line(line)
            if n:
                normalized.append(n)
                line_nums.append(i)

        for i in range(len(normalized) - window_size + 1):
            window = "\n".join(normalized[i:i + window_size])
            h = hashlib.md5(window.encode()).hexdigest()
            location = {"file": file_info["path"], "startLine": line_nums[i], "endLine": line_nums[i + window_size - 1]}
            hash_map.setdefault(h, []).append(location)

    groups = []
    seen_hashes = set()
    for h, locations in hash_map.items():
        if len(locations) < 2:
            continue
        unique_files = set(loc["file"] for loc in locations)
        if len(unique_files) < 2:
            continue
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        groups.append({
            "hash": h,
            "lineCount": window_size,
            "locations": _deduplicate_locations(locations),
        })

    groups.sort(key=lambda g: g["lineCount"] * len(g["locations"]), reverse=True)
    groups = _merge_adjacent_groups(groups)
    groups = groups[:50]

    total_lines = sum(g["lineCount"] * len(g["locations"]) for g in groups)
    return {
        "totalGroups": len(groups),
        "totalDuplicateLines": total_lines,
        "groups": groups,
    }


def _deduplicate_locations(locations):
    seen = set()
    result = []
    for loc in locations:
        key = (loc["file"], loc["startLine"])
        if key not in seen:
            seen.add(key)
            result.append(loc)
    return result[:10]


def _merge_adjacent_groups(groups):
    merged = []
    seen_file_ranges = set()
    for group in groups:
        key = tuple((loc["file"], loc["startLine"]) for loc in group["locations"][:3])
        if key not in seen_file_ranges:
            seen_file_ranges.add(key)
            merged.append(group)
    return merged


def detect_unused_imports(files):
    result_files = []
    total_unused = 0

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
        except (OSError, PermissionError):
            continue

        lines = content.split("\n")
        unused = []

        for line_num, line in enumerate(lines, 1):
            for pattern in IMPORT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                raw = match.group(1)
                if "," in raw or "{" in line:
                    symbols = [s.strip().split(" as ")[-1].strip() for s in raw.split(",")]
                else:
                    symbols = [raw.strip()]

                rest_of_file = "\n".join(lines[line_num:])
                for symbol in symbols:
                    if not symbol or symbol == "type":
                        continue
                    if not re.search(r"\b" + re.escape(symbol) + r"\b", rest_of_file):
                        unused.append({"symbol": symbol, "line": line_num})

        if unused:
            result_files.append({"file": file_info["path"], "imports": unused})
            total_unused += len(unused)

    return {
        "totalFiles": len(result_files),
        "totalUnused": total_unused,
        "files": result_files[:50],
    }
