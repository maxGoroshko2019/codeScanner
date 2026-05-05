# Code Scanner CLI — Design Spec

**Date:** 2026-05-05
**Target codebase:** `C:\Projects\mdc-excel-addin` (TypeScript/Nx monorepo, ~14,800 TS files)
**Language:** Python (zero/minimal external dependencies)
**Architecture:** Single-file core with separate report generators

---

## File Structure

```
scanner.py          — CLI entry point, file traversal, all analysis logic
report_html.py      — HTML report generator (self-contained single file output)
report_md.py        — Markdown report generator
scan-results/       — output directory (gitignored)
.gitignore          — ignores scan-results/ directory
CLAUDE.md           — ground rules for agent collaboration
.claude/commands/scan-and-report.md — custom feedback loop command
```

---

## CLI Interface

```
python scanner.py <directory> [options]
```

**Arguments:**
- `<directory>` — path to codebase to scan (required)

**Options:**
- `--output-dir <path>` — where to write reports (default: `./scan-results/`)
- `--format json|md|html|all` — which reports to generate (default: `all`)
- `--ignore <pattern>` — additional ignore patterns (repeatable)

**Built-in ignore list:**
- `node_modules`, `.git`, `dist`, `build`, `__pycache__`, `.nx/cache`

---

## File Traversal

Walk directory recursively, skipping ignored patterns.

**Language detection by extension:**
- Deep analysis (complexity, security, smells): `.ts`, `.tsx`, `.js`, `.jsx`
- Basic LOC only: `.html`, `.css`, `.json`, `.md`, `.py`, all others

**Per-file metrics:**
- Lines of code (non-blank, non-comment)
- Comment lines (single-line `//` and multi-line `/* */`)
- Blank lines
- Total lines

---

## Analysis Features

### 1. Cyclomatic Complexity (TS/JS only)

**Function detection** (regex-based):
- `function name(`
- `const name = (`  / `let name = (` (arrow functions)
- Method declarations: `name(` inside class bodies
- Arrow functions assigned to variables

**Decision points counted:**
- `if`, `else if`, `while`, `for`, `for...of`, `for...in`
- `case` (in switch)
- `catch`
- `&&`, `||`, `??`
- Ternary `?` (when used as conditional operator)

**Formula:** complexity = 1 + count of decision points per function

**Threshold:** Flag functions with complexity > 10

### 2. Security Scanning (TS/JS only)

**Patterns detected:**

| Category | Pattern | Severity |
|----------|---------|----------|
| Hardcoded secrets | Variables named `key`, `secret`, `token`, `password`, `apiKey` assigned string literals | High |
| AWS keys | `AKIA[0-9A-Z]{16}` | High |
| Private keys | `-----BEGIN.*PRIVATE KEY-----` | High |
| Dangerous functions | `eval(`, `Function(`, `innerHTML =`, `dangerouslySetInnerHTML` | Medium |
| Non-HTTPS URLs | `http://` in string literals (excluding localhost) | Low |
| Disabled lint rules | `eslint-disable.*security` | Low |

**Output per issue:** file path, line number, severity, category, description

### 3. Code Smell Detection (TS/JS only)

| Smell | Threshold | Severity |
|-------|-----------|----------|
| Long function | > 50 lines | Medium |
| Deep nesting | > 4 levels of `{` depth | High |
| Long parameter list | > 5 parameters | Medium |
| Large file | > 300 lines of code | Low |

**Output per smell:** file path, line number, type, severity, details (e.g., "function `processData` is 87 lines")

---

## Quality Score

**Formula:** weighted score from 0 to 100

| Factor | Weight | Scoring |
|--------|--------|---------|
| Complexity | 40% | Penalize: (flagged functions / total functions) ratio |
| Security issues | 30% | Penalize: high=10pts, medium=5pts, low=2pts, capped at 30 |
| Code smells | 30% | Penalize: (smells count / file count) ratio |

Each factor starts at 100 and deductions are applied, then weighted.

**Letter grade:**
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: < 60

---

## Report Formats

### JSON (`scan-results/report.json`)

```json
{
  "scanId": "uuid-v4",
  "timestamp": "2026-05-05T14:30:00Z",
  "repository": {
    "path": "C:\\Projects\\mdc-excel-addin",
    "totalFiles": 15100,
    "totalLines": 450000,
    "languages": {
      "TypeScript": { "files": 14833, "lines": 420000 },
      "JavaScript": { "files": 228, "lines": 15000 },
      "HTML": { "files": 44, "lines": 5000 },
      "CSS": { "files": 17, "lines": 3000 },
      "Other": { "files": 50, "lines": 7000 }
    }
  },
  "files": [
    {
      "path": "apps/api-core/src/handlers/getDataPoints/getDataPoints.handler.ts",
      "language": "TypeScript",
      "metrics": {
        "loc": 120,
        "comments": 15,
        "blanks": 20,
        "total": 155
      }
    }
  ],
  "analysis": {
    "complexity": {
      "totalFunctions": 500,
      "flaggedFunctions": 12,
      "functions": [
        {
          "file": "...",
          "name": "processData",
          "line": 45,
          "complexity": 14
        }
      ]
    },
    "security": {
      "issues": [
        {
          "file": "...",
          "line": 23,
          "severity": "high",
          "category": "hardcoded_secret",
          "description": "Possible API key assigned to variable 'apiKey'"
        }
      ],
      "counts": { "high": 2, "medium": 5, "low": 10 }
    },
    "smells": {
      "issues": [
        {
          "file": "...",
          "line": 10,
          "type": "long_function",
          "severity": "medium",
          "details": "Function 'handleRequest' is 87 lines"
        }
      ],
      "summary": {
        "long_functions": 8,
        "deep_nesting": 3,
        "long_params": 5,
        "large_files": 12
      }
    }
  },
  "qualityScore": 82,
  "grade": "B"
}
```

### Markdown (`scan-results/report.md`)

Sections:
1. Summary table (files, lines, languages, quality score/grade)
2. Top 10 most complex functions (table: file, function, complexity)
3. Security issues (grouped by severity, table format)
4. Code smells summary (counts by type + top offenders)

### HTML (`scan-results/report.html`)

Single self-contained file. No external dependencies.

Sections:
1. Header dashboard: total files, LOC, quality score (large, color-coded), letter grade
2. Language distribution bar chart (vanilla JS, same style as existing `index.html`)
3. Top complex functions table (sortable)
4. Security issues table (color-coded by severity)
5. Code smells table
6. Complexity distribution chart (histogram of function complexities)

Styling: clean, professional, similar to existing coffee shop dashboard aesthetic.

---

## Infrastructure Artifacts

### CLAUDE.md

Starting ground rules:
- Run `python scanner.py C:\Projects\mdc-excel-addin` to test changes — verify JSON output is valid before committing
- TypeScript analysis is regex-based, not AST — don't attempt to parse type annotations for complexity
- HTML report must be fully self-contained — no CDN dependencies, no external files
- (Additional rules added during implementation as correction cycles emerge)

### Custom Command (`.claude/commands/scan-and-report.md`)

```
Run the scanner on C:\Projects\mdc-excel-addin, then:
1. Validate the JSON output is parseable (python -c "import json; json.load(open('scan-results/report.json'))")
2. Check that the HTML report file was generated and is non-empty
3. Report the quality score and grade
4. If there are errors in any step, fix the scanner code and re-run
```

### Feedback Loop

Development workflow:
1. Implement/modify feature
2. Run scanner against `mdc-excel-addin`
3. Inspect output for correctness
4. Fix issues found
5. Re-run to confirm fix

---

## Performance Considerations

The target codebase has ~15,000 files. The scanner must:
- Skip binary files (detect by extension or null-byte check)
- Stream file processing (don't load all files into memory at once)
- Cap detailed `files` array in JSON to top 100 files by issue count (aggregate totals in `repository` remain complete)
- Print progress indicator for large scans (file count / total)

---

## Out of Scope

- AST-based parsing for TypeScript (would require `tree-sitter` or Node.js subprocess)
- Git blame integration
- Historical trend tracking
- IDE integrations
- Remote repository scanning
