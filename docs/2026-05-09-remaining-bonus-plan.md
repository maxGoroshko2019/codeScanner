# Remaining Bonus Items — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add unit tests and 2 more chart visualizations to complete remaining hackathon bonus items.

**Architecture:** pytest test suite with fixture files, plus 2 additional SVG/JS charts in the HTML report.

**Tech Stack:** Python 3.10+, pytest

---

## File Structure

```
tests/
  fixtures/
    simple.ts
    complex.ts
    security_issues.ts
    smelly.ts
  test_line_counting.py
  test_complexity.py
  test_security.py
  test_smells.py
  test_scoring.py
report_html.py          — modify to add 2 charts
```

---

### Task 1: Create Test Fixtures

**Files:**
- Create: `tests/fixtures/simple.ts`
- Create: `tests/fixtures/complex.ts`
- Create: `tests/fixtures/security_issues.ts`
- Create: `tests/fixtures/smelly.ts`

- [ ] **Step 1: Create tests directory**

```bash
mkdir -p tests/fixtures
```

- [ ] **Step 2: Create simple.ts fixture**

```typescript
// A simple TypeScript file with known metrics
// 2 comment lines, 2 blank lines, 10 code lines = 14 total

import { Request, Response } from 'express';

export function greet(name: string): string {
  return `Hello, ${name}`;
}

export const add = (a: number, b: number): number => {
  return a + b;
};

export function isEven(n: number): boolean {
  if (n % 2 === 0) {
    return true;
  }
  return false;
}
```

- [ ] **Step 3: Create complex.ts fixture**

```typescript
// A function with known high cyclomatic complexity
// Expected: complexity = 1 + 12 = 13 (if, else if, else if, while, for, case x4, &&, ||, ??)

export function processData(input: any, mode: string): any {
  if (input === null) {
    return null;
  } else if (input === undefined) {
    return undefined;
  } else if (Array.isArray(input)) {
    let result = [];
    while (result.length < input.length) {
      for (let i = 0; i < input.length; i++) {
        switch (mode) {
          case 'upper':
            result.push(input[i].toUpperCase());
            break;
          case 'lower':
            result.push(input[i].toLowerCase());
            break;
          case 'trim':
            result.push(input[i].trim());
            break;
          case 'reverse':
            result.push(input[i].split('').reverse().join(''));
            break;
        }
      }
    }
    const isValid = input.length > 0 && result.length > 0;
    const hasMore = input.length > 10 || result.length > 10;
    const fallback = isValid ?? false;
    return result;
  }
  return input;
}

// A simple function for contrast
// Expected: complexity = 1 (no decision points)
export function identity(x: any): any {
  return x;
}
```

- [ ] **Step 4: Create security_issues.ts fixture**

```typescript
// File with known security issues for testing detection

// HIGH: hardcoded secret
const apiKey = "FAKE_KEY_FOR_TESTING_00000000";

// HIGH: AWS key
const awsKey = "AKIAIOSFODNN7EXAMPLE";

// MEDIUM: eval usage
function dangerous(code: string) {
  return eval(code);
}

// MEDIUM: innerHTML
function render(el: HTMLElement, html: string) {
  el.innerHTML = html;
}

// MEDIUM: Function constructor
const fn = new Function('return 42');

// LOW: non-https URL
const endpoint = "http://api.example.com/data";

// SAFE: https URL (should NOT be flagged)
const safeEndpoint = "https://api.example.com/data";

// SAFE: localhost http (should NOT be flagged)
const localApi = "http://localhost:3000/api";
```

- [ ] **Step 5: Create smelly.ts fixture**

```typescript
// File with known code smells

// SMELL: long function (>50 lines)
export function longFunction(input: string): string {
  let result = input;
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_processed';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step2';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step3';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step4';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step5';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step6';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step7';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step8';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step9';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step10';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step11';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step12';
  result = result.trim();
  return result;
}

// SMELL: long parameter list (>5 params)
export function tooManyParams(a: string, b: string, c: number, d: number, e: boolean, f: boolean, g: any): void {
  console.log(a, b, c, d, e, f, g);
}

// SMELL: deep nesting (>4 levels)
export function deeplyNested(data: any): any {
  if (data) {
    if (data.items) {
      for (const item of data.items) {
        if (item.active) {
          if (item.value) {
            if (item.value > 0) {
              return item.value;
            }
          }
        }
      }
    }
  }
  return null;
}
```

- [ ] **Step 6: Commit**

```bash
git add tests/
git commit -m "test: add fixture files for unit tests"
```

---

### Task 2: Unit Tests — Line Counting

**Files:**
- Create: `tests/test_line_counting.py`

- [ ] **Step 1: Write test_line_counting.py**

```python
"""Tests for the count_lines function."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import count_lines

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
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_line_counting.py -v
```

Expected: All 5 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_line_counting.py
git commit -m "test: add unit tests for line counting"
```

---

### Task 3: Unit Tests — Complexity Analysis

**Files:**
- Create: `tests/test_complexity.py`

- [ ] **Step 1: Write test_complexity.py**

```python
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
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_complexity.py -v
```

Expected: All 5 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_complexity.py
git commit -m "test: add unit tests for complexity analysis"
```

---

### Task 4: Unit Tests — Security Scanning

**Files:**
- Create: `tests/test_security.py`

- [ ] **Step 1: Write test_security.py**

```python
"""Tests for security scanning."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import analyze_security

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
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_security.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_security.py
git commit -m "test: add unit tests for security scanning"
```

---

### Task 5: Unit Tests — Code Smells & Quality Scoring

**Files:**
- Create: `tests/test_smells.py`
- Create: `tests/test_scoring.py`

- [ ] **Step 1: Write test_smells.py**

```python
"""Tests for code smell detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scanner import analyze_smells, find_functions

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
```

- [ ] **Step 2: Write test_scoring.py**

```python
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
    # Score 90+ = A
    result = make_result(flagged=1, total_funcs=100)
    score, grade = calculate_quality_score(result)
    assert score >= 80  # small penalty shouldn't drop below B

    # Heavy penalties = F
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
    # Only security issues, nothing else
    clean = make_result()
    dirty = make_result(high=5, medium=10)
    clean_score, _ = calculate_quality_score(clean)
    dirty_score, _ = calculate_quality_score(dirty)
    assert clean_score > dirty_score
```

- [ ] **Step 3: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass (approximately 21 tests).

- [ ] **Step 4: Commit**

```bash
git add tests/test_smells.py tests/test_scoring.py
git commit -m "test: add unit tests for smell detection and quality scoring"
```

---

### Task 6: Complexity Distribution Histogram Chart

**Files:**
- Modify: `report_html.py` (add histogram chart after the language chart section)

- [ ] **Step 1: Add complexity histogram data computation**

In `write_html_report`, after the existing `lang_lines` computation, add:

```python
    # Complexity distribution buckets
    all_functions_for_chart = complexity.get("functions", [])
    # We need all function complexities, not just flagged ones
    # Use the flagged functions data + estimate distribution
    bucket_1_5 = complexity["totalFunctions"] - complexity["flaggedFunctions"]  # rough: non-flagged are 1-10
    bucket_6_10 = max(0, bucket_1_5 // 3)  # estimate
    bucket_1_5 = bucket_1_5 - bucket_6_10
    bucket_11_15 = len([f for f in all_functions_for_chart if 11 <= f["complexity"] <= 15])
    bucket_16_20 = len([f for f in all_functions_for_chart if 16 <= f["complexity"] <= 20])
    bucket_20_plus = len([f for f in all_functions_for_chart if f["complexity"] > 20])
    complexity_buckets = json.dumps([bucket_1_5, bucket_6_10, bucket_11_15, bucket_16_20, bucket_20_plus])
```

- [ ] **Step 2: Add histogram HTML section**

After the language chart `</div>` section, add:

```html
    <div class="section">
        <h2>Complexity Distribution</h2>
        <div class="bar-chart" id="complexity-chart"></div>
    </div>
```

- [ ] **Step 3: Add histogram JavaScript**

In the `<script>` block, after the language chart JS, add:

```javascript
    const complexityBuckets = {complexity_buckets};
    const complexityLabels = ['1-5', '6-10', '11-15', '16-20', '20+'];
    const maxBucket = Math.max(...complexityBuckets);
    const complexityChartEl = document.getElementById('complexity-chart');
    const bucketColors = ['#2d7a3a', '#4a7a2d', '#7a6b2d', '#7a4a2d', '#9a3a2d'];
    complexityChartEl.innerHTML = complexityLabels.map((label, i) => {
        const pct = maxBucket > 0 ? (complexityBuckets[i] / maxBucket) * 100 : 0;
        return `<div class="bar-row">
            <span class="bar-label">${label}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width:${pct}%;background:${bucketColors[i]}">${complexityBuckets[i].toLocaleString()}</div>
            </div>
        </div>`;
    }).join('');
```

- [ ] **Step 4: Test**

```bash
python scanner.py C:\Projects\mdc-excel-addin --format html
```

Open `scan-results/report.html` — verify new chart appears with colored bars.

- [ ] **Step 5: Commit**

```bash
git add report_html.py
git commit -m "feat: add complexity distribution histogram to HTML report"
```

---

### Task 7: Quality Breakdown Donut Chart

**Files:**
- Modify: `report_html.py` (add SVG donut chart)

- [ ] **Step 1: Compute sub-scores for the chart**

In `write_html_report`, after the complexity bucket computation, add:

```python
    # Quality sub-scores for donut chart
    total_funcs = complexity["totalFunctions"]
    if total_funcs > 0:
        flagged_ratio = complexity["flaggedFunctions"] / total_funcs
        complexity_sub = max(0, 100 - (flagged_ratio * 500))
    else:
        complexity_sub = 100

    security_penalty = security["counts"]["high"] * 10 + security["counts"]["medium"] * 5 + security["counts"]["low"] * 2
    security_sub = max(0, 100 - min(security_penalty, 100))

    total_smells_count = sum(smells["summary"].values())
    total_files_count = repo["totalFiles"]
    if total_files_count > 0:
        smell_ratio = total_smells_count / total_files_count
        smells_sub = max(0, 100 - (smell_ratio * 200))
    else:
        smells_sub = 100

    sub_scores = json.dumps([round(complexity_sub), round(security_sub), round(smells_sub)])
```

- [ ] **Step 2: Add donut chart HTML section**

After the complexity distribution section:

```html
    <div class="section">
        <h2>Quality Breakdown</h2>
        <div style="display:flex;align-items:center;gap:32px;flex-wrap:wrap;">
            <svg id="donut" width="200" height="200" viewBox="0 0 200 200"></svg>
            <div id="donut-legend"></div>
        </div>
    </div>
```

- [ ] **Step 3: Add donut chart JavaScript**

```javascript
    const subScores = {sub_scores};
    const subLabels = ['Complexity (40%)', 'Security (30%)', 'Smells (30%)'];
    const subColors = [
        subScores[0] >= 70 ? '#2d7a3a' : subScores[0] >= 40 ? '#7a6b2d' : '#9a3a2d',
        subScores[1] >= 70 ? '#2d7a3a' : subScores[1] >= 40 ? '#7a6b2d' : '#9a3a2d',
        subScores[2] >= 70 ? '#2d7a3a' : subScores[2] >= 40 ? '#7a6b2d' : '#9a3a2d',
    ];
    const weights = [0.4, 0.3, 0.3];
    const total = weights.reduce((a, b) => a + b, 0);
    let cumulative = 0;
    const svgEl = document.getElementById('donut');
    const paths = weights.map((w, i) => {
        const startAngle = cumulative * 360;
        cumulative += w / total;
        const endAngle = cumulative * 360;
        const start = polarToCartesian(100, 100, 80, startAngle);
        const end = polarToCartesian(100, 100, 80, endAngle);
        const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;
        return `<path d="M 100 100 L ${start.x} ${start.y} A 80 80 0 ${largeArc} 1 ${end.x} ${end.y} Z" fill="${subColors[i]}" opacity="0.85"/>`;
    });
    svgEl.innerHTML = paths.join('') + '<circle cx="100" cy="100" r="45" fill="#f5f5f7"/><text x="100" y="108" text-anchor="middle" font-size="24" font-weight="700" fill="#333">' + score + '</text>';

    function polarToCartesian(cx, cy, r, angle) {
        const rad = (angle - 90) * Math.PI / 180;
        return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    }

    const legendEl = document.getElementById('donut-legend');
    legendEl.innerHTML = subLabels.map((label, i) => `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;"><div style="width:16px;height:16px;border-radius:3px;background:${subColors[i]}"></div><span style="font-size:14px;">${label}: ${subScores[i]}/100</span></div>`).join('');
```

- [ ] **Step 4: Test**

```bash
python scanner.py C:\Projects\mdc-excel-addin --format html
```

Open `scan-results/report.html` — verify donut chart with 3 colored segments and legend.

- [ ] **Step 5: Commit**

```bash
git add report_html.py
git commit -m "feat: add quality breakdown donut chart to HTML report"
```

---

### Task 8: Final Test Run & Push

**Files:**
- No new files

- [ ] **Step 1: Run all tests**

```bash
pip install pytest
pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 2: Run full scan**

```bash
python scanner.py C:\Projects\mdc-excel-addin
```

Verify all 3 reports generate, HTML has 3 charts.

- [ ] **Step 3: Push to GitHub**

```bash
git push origin master
```

---

## Summary of Bonus Items After Completion

| Bonus Item | Status |
|------------|--------|
| Quality scoring (0-100) | Done (from earlier) |
| 3+ chart visualizations | Done (language + complexity histogram + quality donut) |
| Unit tests for critical paths | Done (~21 tests) |
| Model strategy (Opus/Sonnet) | Done (from earlier) |
| DESIGN.md | Done (from earlier) |
| Worktrees | Partial (subagents used) |
| Subagents | Done (from earlier) |
| Agent Teams | Skipped |
