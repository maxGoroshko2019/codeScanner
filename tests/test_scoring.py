"""Tests for quality scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import calculate_quality_score


def make_result(flagged=0, total_funcs=100, high=0, medium=0, low=0, smells=0, files=100):
    return {
        "repository": {"totalFiles": files},
        "analysis": {
            "complexity": {"totalFunctions": total_funcs, "flaggedFunctions": flagged, "functions": []},
            "security": {"issues": [], "counts": {"high": high, "medium": medium, "low": low}},
            "smells": {"issues": [], "summary": {"long_functions": smells, "deep_nesting": 0, "long_params": 0, "large_files": 0}},
        },
    }


def test_perfect_score():
    result = make_result(flagged=0, high=0, medium=0, low=0, smells=0)
    score, grade = calculate_quality_score(result)
    assert score == 100
    assert grade == "A"


def test_grade_boundaries():
    result = make_result(flagged=1, total_funcs=100)
    score, grade = calculate_quality_score(result)
    assert score >= 80

    result = make_result(flagged=50, total_funcs=100, high=10, medium=20, low=50, smells=200, files=100)
    score, grade = calculate_quality_score(result)
    assert grade in ("D", "F")


def test_score_between_0_and_100():
    result = make_result(flagged=100, total_funcs=100, high=100, medium=100, low=100, smells=1000, files=10)
    score, grade = calculate_quality_score(result)
    assert 0 <= score <= 100


def test_no_functions_gives_full_complexity_score():
    result = make_result(flagged=0, total_funcs=0)
    score, grade = calculate_quality_score(result)
    assert score == 100


def test_security_weight():
    clean = make_result()
    dirty = make_result(high=5, medium=10)
    clean_score, _ = calculate_quality_score(clean)
    dirty_score, _ = calculate_quality_score(dirty)
    assert clean_score > dirty_score
