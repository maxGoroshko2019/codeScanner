"""Tests for complexity analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import find_functions, analyze_complexity

FIXTURES = Path(__file__).parent / "fixtures"


def test_find_functions_detects_all_in_simple():
    with open(FIXTURES / "simple.ts", "r") as f:
        lines = f.read().split("\n")
    funcs = find_functions(lines, "simple.ts")
    names = [fn["name"] for fn in funcs]
    assert "greet" in names
    assert "add" in names
    assert "isEven" in names


def test_simple_functions_low_complexity():
    with open(FIXTURES / "simple.ts", "r") as f:
        lines = f.read().split("\n")
    funcs = find_functions(lines, "simple.ts")
    for fn in funcs:
        assert fn["complexity"] <= 5, f"{fn['name']} has complexity {fn['complexity']}"


def test_complex_function_high_complexity():
    with open(FIXTURES / "complex.ts", "r") as f:
        lines = f.read().split("\n")
    funcs = find_functions(lines, "complex.ts")
    process_data = next(fn for fn in funcs if fn["name"] == "processData")
    assert process_data["complexity"] > 10


def test_identity_function_minimal_complexity():
    with open(FIXTURES / "complex.ts", "r") as f:
        lines = f.read().split("\n")
    funcs = find_functions(lines, "complex.ts")
    identity = next(fn for fn in funcs if fn["name"] == "identity")
    assert identity["complexity"] == 1


def test_analyze_complexity_returns_correct_structure():
    files = [{
        "absolute_path": str(FIXTURES / "complex.ts"),
        "path": "complex.ts",
        "metrics": {"loc": 50, "comments": 5, "blanks": 5, "total": 60},
    }]
    result = analyze_complexity(files)
    assert "totalFunctions" in result
    assert "flaggedFunctions" in result
    assert "functions" in result
    assert result["totalFunctions"] >= 2
