# Code Scanner — Presentation Guide

> A quick-reference guide for presenting the code scanner tool and interpreting its results.

---

## Slide 1: What Is It?

**Code Scanner** is a Python CLI tool that analyzes TypeScript/JavaScript codebases and produces a quality report with a single score (0-100) plus detailed breakdowns.

**One command, three reports:**

```bash
python scanner.py C:\Projects\mdc-excel-addin
```

Outputs: `report.json` (data), `report.md` (readable), `report.html` (visual dashboard)

**Key value:** Instant, objective code quality assessment without manual review. Identifies exactly where to focus refactoring effort.

---

## Slide 2: The Score

```
 ┌─────────────────────────────────────┐
 │         Quality Score: 96/100       │
 │              Grade: A               │
 └─────────────────────────────────────┘
```

The score is weighted across three dimensions:
- **Complexity** (40%) — Are functions too convoluted?
- **Security** (30%) — Are there hardcoded secrets or dangerous patterns?
- **Code Smells** (30%) — Long functions, deep nesting, bloated files?

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 90-100 | Excellent — well-maintained |
| B | 80-89 | Good — minor improvements possible |
| C | 70-79 | Fair — notable technical debt |
| D | 60-69 | Poor — needs attention |
| F | 0-59 | Critical — significant risk |

---

## Slide 3: Dashboard Overview (from HTML report)

Real numbers from mdc-excel-addin scan:

```
 ┌──────────┬───────────┬───────────┬──────────┬───────────┬───────────┐
 │  2,043   │  101,428  │    123    │    0     │     4     │    15     │
 │  Files   │   LOC     │ Functions │Complex>10│ Security  │  Smells   │
 └──────────┴───────────┴───────────┴──────────┴───────────┴───────────┘
```

At a glance: 2,043 files scanned, zero overly-complex functions, only 4 minor security findings.

---

## Slide 4: Complexity Analysis

**What it measures:** Cyclomatic complexity — number of decision paths through a function (if/else, loops, switch cases, logical operators).

**Threshold:** Functions scoring >10 are flagged.

**Our result:** 0 of 123 functions flagged (0.0%)

**Industry benchmark:** Well-maintained codebases typically have 3-8% of functions exceeding threshold. Our codebase scores "excellent."

**What to look for in bad scans:**
```
  getSelectorSpecificity() — complexity 9011 (bundled code!)
  processData()            — complexity 42 (needs splitting)
```

---

## Slide 5: Security Scanning

**What it detects:**
| Category | Severity | Example |
|----------|----------|---------|
| Hardcoded secrets | HIGH | `apiKey = "AKIAIOSFODNN..."` |
| AWS access keys | HIGH | `AKIA` pattern |
| Private keys | HIGH | `-----BEGIN PRIVATE KEY-----` |
| eval() / innerHTML | MEDIUM | Direct code injection vectors |
| Non-HTTPS URLs | LOW | `http://api.example.com` |

**Our result:**
- High: 0
- Medium: 1 (Function constructor in a type definition)
- Low: 3 (HTTP URLs in external type libs)

**Smart filtering:** Automatically skips `.test.ts` files (test fixtures are not real secrets) and minified bundles.

---

## Slide 6: Code Smells

**What it detects:**

| Smell | Threshold | Why it matters |
|-------|-----------|----------------|
| Long Functions | >50 lines | Hard to test, hard to understand |
| Deep Nesting | >4 levels | High cognitive load |
| Long Parameters | >5 params | Sign of poor abstraction |
| Large Files | >300 LOC | Likely doing too many things |

**Our result:**
- Long functions: 1
- Deep nesting: 11
- Long params: 0
- Large files: 3

The 11 deep-nesting findings are the main area for improvement.

---

## Slide 7: Duplicate Code Detection

**How it works:** Scans all source files using a sliding-window hash algorithm. Identifies blocks of 5+ identical lines across different files.

**Our result:** 50 duplicate groups totaling 640 lines

**What this means:** There are repeated patterns that could be extracted into shared utilities. The scanner identifies exact file locations so developers know where to look.

---

## Slide 8: Historical Trends

Every scan saves a snapshot. On subsequent scans, the tool shows:

```
 ┌────────────────────────────────────────────┐
 │  Trend: +49 points since last scan         │
 │                                            │
 │  Category    Previous  Current   Delta     │
 │  Complexity     682        0      -682     │
 │  Security        15        4       -11     │
 │  Smells         819       15      -804     │
 └────────────────────────────────────────────┘
```

This shows the impact of our accuracy fixes — the massive drop is from excluding minified/bundled code that was creating false positives.

---

## Slide 9: Remediation Roadmap

The scanner generates a prioritized action list:

```
 ┌─────────────────────────────────────────────────────┐
 │  Priority  Action                        Effort     │
 │  ────────  ─────────────────────────     ───────    │
 │  1.        Consolidate 50 duplicate      medium     │
 │            code blocks (640 lines)                  │
 └─────────────────────────────────────────────────────┘
```

Items are ranked by estimated score impact. For our A-grade codebase, the only suggestion is consolidating duplicates — everything else is already clean.

---

## Slide 10: How to Use It

**Basic scan:**
```bash
python scanner.py <path-to-repo>
```

**Custom thresholds:**
```bash
python scanner.py <path> --complexity-threshold 12 --large-file-threshold 500
```

**Quick JSON only (fastest):**
```bash
python scanner.py <path> --format json
```

**Skip slow features:**
```bash
python scanner.py <path> --no-duplicates --no-history
```

---

## Slide 11: Architecture (for technical audience)

```
scanner.py          CLI + file traversal (293 lines)
analyzers.py        Complexity, security, smells (250 lines)
detection.py        Duplicate code + unused imports (180 lines)
trends.py           Historical comparison (120 lines)
roadmap.py          Remediation suggestions (100 lines)
report_html.py      Self-contained HTML dashboard
report_md.py        Markdown report
```

**Key design decisions:**
- Regex-based analysis (no AST) — fast, works on any TS/JS
- Self-contained HTML — no CDN dependencies, works offline
- Minified/bundled code auto-detected and skipped
- Test files excluded from security scanning

---

## Talking Points

1. **"What problem does this solve?"** — Gives teams an objective, automated quality baseline without relying on code reviews alone. One number (the score) makes it easy to track over time.

2. **"How accurate is it?"** — It filters out false positives (bundled code, test fixtures, type definitions) that inflate results. The current scan shows real source quality only.

3. **"How fast is it?"** — Scans 2,000+ files in ~10 seconds. No build step required.

4. **"Can it run in CI/CD?"** — Yes. The JSON output can be parsed by any pipeline. Could gate PRs on score regression.

5. **"What's the ROI?"** — The roadmap tells developers exactly where to invest effort for maximum quality gain. No guessing.
