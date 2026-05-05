Run the code scanner and validate all outputs:

1. Run: `python scanner.py C:\Projects\mdc-excel-addin`
2. Validate JSON: `python -c "import json; d=json.load(open('scan-results/report.json')); print(f\"Score: {d['qualityScore']}/100 ({d['grade']})\")"` 
3. Check HTML report exists and is non-empty: `test -s scan-results/report.html && echo "HTML OK" || echo "HTML MISSING"`
4. Check Markdown report exists and is non-empty: `test -s scan-results/report.md && echo "MD OK" || echo "MD MISSING"`
5. Report the quality score and grade
6. If any step fails, diagnose and fix the issue, then re-run from step 1
