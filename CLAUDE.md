# Ground Rules

- Run `python scanner.py C:\Projects\mdc-excel-addin` to test changes — verify JSON output is valid before committing
- TypeScript analysis is regex-based, not AST — don't attempt to parse type annotations for complexity
- HTML report must be fully self-contained — no CDN dependencies, no external files
- Keep scanner.py under 400 lines — if it grows larger, the analysis functions need refactoring into helpers
- Always test with --format json first (fastest), then validate other formats
