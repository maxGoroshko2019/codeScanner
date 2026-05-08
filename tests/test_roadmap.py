"""Tests for remediation roadmap."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from roadmap import generate_roadmap


def _make_result(flagged=5, functions=None, high=0, medium=0, low=0, smells=None, duplicates=None, unused=None):
    if functions is None:
        functions = [{"file": "src/a.ts", "name": "bigFunc", "line": 10, "complexity": 25, "length": 80}]
    if smells is None:
        smells = {"long_functions": 3, "deep_nesting": 1, "long_params": 0, "large_files": 0}
    if duplicates is None:
        duplicates = {"totalGroups": 2, "totalDuplicateLines": 30, "groups": []}
    if unused is None:
        unused = {"totalFiles": 5, "totalUnused": 12, "files": []}
    return {
        "repository": {"totalFiles": 100, "totalLines": 5000},
        "analysis": {
            "complexity": {"totalFunctions": 100, "flaggedFunctions": flagged, "functions": functions},
            "security": {"issues": [], "counts": {"high": high, "medium": medium, "low": low}},
            "smells": {"issues": [], "summary": smells},
            "duplicates": duplicates,
            "unusedImports": unused,
        },
    }


def test_roadmap_returns_up_to_5_items():
    result = _make_result(high=3, flagged=20, smells={"long_functions": 10, "deep_nesting": 5, "long_params": 3, "large_files": 2})
    roadmap = generate_roadmap(result)
    assert len(roadmap) <= 5


def test_roadmap_prioritizes_high_score_gain():
    result = _make_result(high=5)
    roadmap = generate_roadmap(result)
    gains = [item["estimatedScoreGain"] for item in roadmap]
    assert gains == sorted(gains, reverse=True)


def test_roadmap_includes_unused_imports():
    result = _make_result()
    roadmap = generate_roadmap(result)
    categories = [item["category"] for item in roadmap]
    assert "unused_imports" in categories


def test_roadmap_includes_duplicates():
    result = _make_result()
    roadmap = generate_roadmap(result)
    categories = [item["category"] for item in roadmap]
    assert "duplicates" in categories


def test_roadmap_handles_perfect_score():
    result = _make_result(
        flagged=0, functions=[], high=0, medium=0, low=0,
        smells={"long_functions": 0, "deep_nesting": 0, "long_params": 0, "large_files": 0},
        duplicates={"totalGroups": 0, "totalDuplicateLines": 0, "groups": []},
        unused={"totalFiles": 0, "totalUnused": 0, "files": []},
    )
    roadmap = generate_roadmap(result)
    assert roadmap == []


def test_roadmap_items_have_correct_structure():
    result = _make_result()
    roadmap = generate_roadmap(result)
    for item in roadmap:
        assert "priority" in item
        assert "action" in item
        assert "category" in item
        assert "estimatedScoreGain" in item
        assert "effort" in item
        assert "rationale" in item
        assert item["priority"] >= 1
