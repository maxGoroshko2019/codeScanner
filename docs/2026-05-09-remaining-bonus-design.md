# Code Scanner — Remaining Bonus Items Design

**Date:** 2026-05-05 (for implementation 2026-05-09)
**Context:** Core scanner complete. These are the remaining hackathon bonus items.

---

## Items to Complete

### 1. Unit Tests for Critical Paths

**What to test:**
- `count_lines()` — correctly distinguishes code/comments/blanks for TS/JS files
- `find_functions()` — detects function declarations, arrow functions, class methods
- `analyze_complexity()` — correctly calculates cyclomatic complexity for known inputs
- `analyze_security()` — detects each pattern category (secrets, eval, innerHTML, etc.)
- `check_deep_nesting()` — accurately counts brace depth
- `check_long_params()` — catches functions with >5 parameters
- `calculate_quality_score()` — returns expected scores for known inputs

**Approach:**
- Use `pytest` (the only external dependency)
- Create test fixtures: small TypeScript files with known characteristics
- Each test function targets one behavior with a clear assertion
- No mocking needed — these are pure functions that take strings/lists and return dicts

**File structure:**
```
tests/
  fixtures/
    simple.ts          — basic file with known metrics
    complex.ts         — file with high-complexity function
    security_issues.ts — file with known security patterns
    smelly.ts          — file with code smells (deep nesting, long params)
  test_line_counting.py
  test_complexity.py
  test_security.py
  test_smells.py
  test_scoring.py
```

---

### 2. Additional Chart Visualizations (need 2 more for "3+ charts" bonus)

**Current:** 1 chart (language distribution bar chart in HTML report)

**Charts to add:**

**Chart 2: Complexity Distribution Histogram**
- X-axis: complexity ranges (1-5, 6-10, 11-15, 16-20, 20+)
- Y-axis: number of functions in each range
- Shows how most functions are simple, with a tail of complex ones
- Implementation: count functions in each bucket, render as bar chart

**Chart 3: Quality Breakdown Donut/Pie**
- Three segments: Complexity (40%), Security (30%), Smells (30%)
- Each segment colored by its individual score (green=good, red=bad)
- Shows which factor is dragging the overall score down
- Implementation: SVG-based donut chart (no external deps), computed from the three sub-scores

**Both charts go in the HTML report, after the existing language chart.**

---

### 3. Worktrees for Parallel Implementations (optional stretch)

This was about using git worktrees during the build process to run parallel implementations. Since we already used subagents in parallel (Tasks 7+8), and the scanner is complete, this bonus is partially satisfied. 

If desired, a demonstration would be: use `/parallel-implementations 3` to generate 3 variant HTML report designs and pick the best one. This is a process demonstration, not a code task.

---

## Out of Scope

- Agent Teams (experimental feature, not worth the time)
- Major refactoring of existing scanner code
- New analysis features beyond what's built

---

## Dependencies

- `pytest` — install via `pip install pytest`
- No other new dependencies
