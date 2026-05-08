"""Tests for security scanning."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyzers import analyze_security

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_hardcoded_secret():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    categories = [i["category"] for i in result["issues"]]
    assert "hardcoded_secret" in categories


def test_detects_aws_key():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    categories = [i["category"] for i in result["issues"]]
    assert "aws_key" in categories


def test_detects_dangerous_functions():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    categories = [i["category"] for i in result["issues"]]
    assert "dangerous_function" in categories


def test_detects_non_https():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    categories = [i["category"] for i in result["issues"]]
    assert "non_https" in categories


def test_counts_by_severity():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    assert result["counts"]["high"] >= 2
    assert result["counts"]["medium"] >= 2
    assert result["counts"]["low"] >= 1


def test_does_not_flag_https_urls():
    files = [{
        "absolute_path": str(FIXTURES / "security_issues.ts"),
        "path": "security_issues.ts",
        "metrics": {"loc": 30, "comments": 5, "blanks": 3, "total": 38},
    }]
    result = analyze_security(files)
    for issue in result["issues"]:
        if issue["category"] == "non_https":
            assert "https://" not in issue.get("details", "")
