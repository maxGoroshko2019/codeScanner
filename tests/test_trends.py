"""Tests for historical trend comparison."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from trends import compare_to_history, save_to_history


def _make_result(score=80, grade="B", flagged=5, high=0, medium=0, low=0, smells=None):
    if smells is None:
        smells = {"long_functions": 2, "deep_nesting": 1, "long_params": 0, "large_files": 0}
    return {
        "scanId": "test-scan-123",
        "timestamp": "2026-05-08T12:00:00Z",
        "repository": {"path": "C:\\Projects\\test-repo", "totalFiles": 100, "totalLines": 5000, "languages": {}},
        "qualityScore": score,
        "grade": grade,
        "analysis": {
            "complexity": {
                "totalFunctions": 100,
                "flaggedFunctions": flagged,
                "functions": [{"file": "src/a.ts", "name": "complex", "line": 10, "complexity": 15, "length": 60}],
            },
            "security": {"issues": [{"file": "src/b.ts", "line": 5, "severity": "high", "category": "hardcoded_secret", "description": "test"}], "counts": {"high": high, "medium": medium, "low": low}},
            "smells": {"issues": [{"file": "src/c.ts", "line": 1, "type": "large_file", "severity": "low", "details": "test"}], "summary": smells},
        },
    }


def test_no_history_returns_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _make_result()
        trend = compare_to_history(result, tmpdir)
        assert trend is None


def test_score_improvement_shows_positive_delta():
    with tempfile.TemporaryDirectory() as tmpdir:
        prev = _make_result(score=40, grade="F", flagged=10)
        save_to_history(prev, tmpdir)

        current = _make_result(score=60, grade="D", flagged=5)
        trend = compare_to_history(current, tmpdir)
        assert trend is not None
        assert trend["scoreDelta"] == 20


def test_score_regression_shows_negative_delta():
    with tempfile.TemporaryDirectory() as tmpdir:
        prev = _make_result(score=80, grade="B", flagged=3)
        save_to_history(prev, tmpdir)

        current = _make_result(score=60, grade="D", flagged=10)
        trend = compare_to_history(current, tmpdir)
        assert trend["scoreDelta"] == -20


def test_new_issues_detected():
    with tempfile.TemporaryDirectory() as tmpdir:
        prev = _make_result()
        save_to_history(prev, tmpdir)

        current = _make_result()
        current["analysis"]["complexity"]["functions"].append(
            {"file": "src/new.ts", "name": "newFunc", "line": 1, "complexity": 20, "length": 80}
        )
        trend = compare_to_history(current, tmpdir)
        assert len(trend["newIssues"]) > 0


def test_resolved_issues_detected():
    with tempfile.TemporaryDirectory() as tmpdir:
        prev = _make_result()
        save_to_history(prev, tmpdir)

        current = _make_result()
        current["analysis"]["complexity"]["functions"] = []
        current["analysis"]["security"]["issues"] = []
        current["analysis"]["smells"]["issues"] = []
        trend = compare_to_history(current, tmpdir)
        assert len(trend["resolvedIssues"]) > 0


def test_history_file_created_on_first_scan():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _make_result()
        save_to_history(result, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, ".scanner-history.json"))


def test_history_pruned_to_20_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(25):
            result = _make_result(score=50 + i)
            result["scanId"] = f"scan-{i}"
            save_to_history(result, tmpdir)

        with open(os.path.join(tmpdir, ".scanner-history.json"), "r") as f:
            history = json.load(f)
        repo_entries = [e for e in history["entries"] if e["repositoryPath"] == "C:\\Projects\\test-repo"]
        assert len(repo_entries) <= 20


def test_filters_by_repository_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        other_repo = _make_result(score=30)
        other_repo["repository"]["path"] = "C:\\Projects\\other-repo"
        save_to_history(other_repo, tmpdir)

        current = _make_result(score=80)
        trend = compare_to_history(current, tmpdir)
        assert trend is None
