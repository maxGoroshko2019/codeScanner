"""Tests for duplicate code detection and unused imports."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from detection import detect_duplicates, detect_unused_imports

FIXTURES = Path(__file__).parent / "fixtures"


def _make_file_info(fixture_name):
    return {
        "absolute_path": str(FIXTURES / fixture_name),
        "path": fixture_name,
        "metrics": {"loc": 20, "comments": 1, "blanks": 2, "total": 23},
    }


def test_detect_duplicates_finds_exact_copy():
    files = [_make_file_info("duplicates_a.ts"), _make_file_info("duplicates_b.ts")]
    result = detect_duplicates(files, window_size=5)
    assert result["totalGroups"] >= 1


def test_detect_duplicates_returns_correct_structure():
    files = [_make_file_info("duplicates_a.ts"), _make_file_info("duplicates_b.ts")]
    result = detect_duplicates(files, window_size=5)
    assert "totalGroups" in result
    assert "totalDuplicateLines" in result
    assert "groups" in result
    if result["groups"]:
        group = result["groups"][0]
        assert "hash" in group
        assert "lineCount" in group
        assert "locations" in group


def test_detect_duplicates_ignores_short_files():
    files = [{
        "absolute_path": str(FIXTURES / "simple.ts"),
        "path": "simple.ts",
        "metrics": {"loc": 5, "comments": 0, "blanks": 0, "total": 5},
    }]
    result = detect_duplicates(files, window_size=5)
    assert result["totalGroups"] == 0


def test_detect_duplicates_skips_non_ts_files():
    files = [{
        "absolute_path": str(FIXTURES / "duplicates_a.ts"),
        "path": "duplicates_a.json",
        "metrics": {"loc": 20, "comments": 1, "blanks": 2, "total": 23},
    }]
    files[0]["absolute_path"] = files[0]["absolute_path"].replace(".ts", ".json")
    result = detect_duplicates(files, window_size=5)
    assert result["totalGroups"] == 0


def test_detect_duplicates_empty_input():
    result = detect_duplicates([], window_size=5)
    assert result["totalGroups"] == 0
    assert result["totalDuplicateLines"] == 0


def test_unused_imports_detects_unused():
    files = [_make_file_info("unused_imports.ts")]
    result = detect_unused_imports(files)
    assert result["totalUnused"] >= 2
    all_symbols = []
    for f in result["files"]:
        all_symbols.extend(imp["symbol"] for imp in f["imports"])
    assert "useEffect" in all_symbols
    assert "useMemo" in all_symbols


def test_unused_imports_does_not_flag_used():
    files = [_make_file_info("unused_imports.ts")]
    result = detect_unused_imports(files)
    all_symbols = []
    for f in result["files"]:
        all_symbols.extend(imp["symbol"] for imp in f["imports"])
    assert "useState" not in all_symbols


def test_unused_imports_handles_namespace_import():
    files = [_make_file_info("unused_imports.ts")]
    result = detect_unused_imports(files)
    all_symbols = []
    for f in result["files"]:
        all_symbols.extend(imp["symbol"] for imp in f["imports"])
    assert "lodash" in all_symbols


def test_unused_imports_handles_default_import():
    files = [_make_file_info("unused_imports.ts")]
    result = detect_unused_imports(files)
    all_symbols = []
    for f in result["files"]:
        all_symbols.extend(imp["symbol"] for imp in f["imports"])
    assert "axios" in all_symbols


def test_unused_imports_returns_correct_structure():
    files = [_make_file_info("unused_imports.ts")]
    result = detect_unused_imports(files)
    assert "totalFiles" in result
    assert "totalUnused" in result
    assert "files" in result
    if result["files"]:
        entry = result["files"][0]
        assert "file" in entry
        assert "imports" in entry
        assert "symbol" in entry["imports"][0]
        assert "line" in entry["imports"][0]


def test_unused_imports_empty_input():
    result = detect_unused_imports([])
    assert result["totalFiles"] == 0
    assert result["totalUnused"] == 0
