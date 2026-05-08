"""Tests for code smell detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyzers import analyze_smells

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_large_file():
    files = [{
        "absolute_path": str(FIXTURES / "smelly.ts"),
        "path": "smelly.ts",
        "metrics": {"loc": 350, "comments": 5, "blanks": 10, "total": 365},
    }]
    result = analyze_smells(files)
    assert result["summary"]["large_files"] >= 1


def test_detects_deep_nesting():
    files = [{
        "absolute_path": str(FIXTURES / "smelly.ts"),
        "path": "smelly.ts",
        "metrics": {"loc": 80, "comments": 5, "blanks": 5, "total": 90},
    }]
    result = analyze_smells(files)
    assert result["summary"]["deep_nesting"] >= 1


def test_detects_long_params():
    files = [{
        "absolute_path": str(FIXTURES / "smelly.ts"),
        "path": "smelly.ts",
        "metrics": {"loc": 80, "comments": 5, "blanks": 5, "total": 90},
    }]
    result = analyze_smells(files)
    assert result["summary"]["long_params"] >= 1


def test_detects_long_function():
    files = [{
        "absolute_path": str(FIXTURES / "smelly.ts"),
        "path": "smelly.ts",
        "metrics": {"loc": 80, "comments": 5, "blanks": 5, "total": 90},
    }]
    result = analyze_smells(files)
    assert result["summary"]["long_functions"] >= 1


def test_issues_have_correct_structure():
    files = [{
        "absolute_path": str(FIXTURES / "smelly.ts"),
        "path": "smelly.ts",
        "metrics": {"loc": 80, "comments": 5, "blanks": 5, "total": 90},
    }]
    result = analyze_smells(files)
    for issue in result["issues"]:
        assert "file" in issue
        assert "line" in issue
        assert "type" in issue
        assert "severity" in issue
        assert "details" in issue
