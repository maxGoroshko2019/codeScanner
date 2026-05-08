"""Tests for the count_lines function."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import count_lines  # count_lines stays in scanner (traversal logic)

FIXTURES = Path(__file__).parent / "fixtures"


def test_simple_file_totals():
    result = count_lines(FIXTURES / "simple.ts")
    assert result["total"] > 0
    assert result["loc"] > 0
    assert result["loc"] + result["comments"] + result["blanks"] == result["total"]


def test_simple_file_comments():
    result = count_lines(FIXTURES / "simple.ts")
    assert result["comments"] == 2


def test_simple_file_blanks():
    result = count_lines(FIXTURES / "simple.ts")
    assert result["blanks"] >= 2


def test_nonexistent_file():
    result = count_lines(Path("does_not_exist.ts"))
    assert result == {"loc": 0, "comments": 0, "blanks": 0, "total": 0}


def test_loc_excludes_comments_and_blanks():
    result = count_lines(FIXTURES / "complex.ts")
    assert result["loc"] == result["total"] - result["comments"] - result["blanks"]
