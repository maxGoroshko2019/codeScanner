# Code Scan Report

**Quality Score: 96/100 (Grade: A)**

_Typical well-maintained codebases have 3-8% of functions exceeding complexity threshold of 10. Your ratio: 0.0%._

---

## Summary

| Metric | Value |
|--------|-------|
| Path | `C:\Projects\mdc-excel-addin` |
| Total Files | 2,043 |
| Total Lines of Code | 101,428 |
| Functions Analyzed | 123 |
| Complex Functions (>10) | 0 |
| Security Issues | 4 |
| Code Smells | 15 |
| Duplicate Code Groups | 50 |
| Unused Imports | 0 |

## Languages

| Language | Files | Lines |
|----------|-------|-------|
| TypeScript | 1,930 | 50,677 |
| Other | 61 | 4,492 |
| JSON | 26 | 43,954 |
| Markdown | 21 | 1,927 |
| JavaScript | 3 | 353 |
| HTML | 2 | 25 |

## Top Problem Files

| File | Total Issues | Complexity | Security | Smells |
|------|-------------|-----------|----------|--------|
| `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.ts` | 3 | 0 | 1 | 2 |
| `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts` | 2 | 0 | 0 | 2 |
| `apps/plugin/src/federated/nanofrontendTypes/libs/ag-grid/ag-grid-community/core/entities/gridOptions.d.ts` | 1 | 0 | 1 | 0 |
| `apps/plugin/src/federated/nanofrontendTypes/libs/ag-grid/ag-charts-community/src/util/dom.d.ts` | 1 | 0 | 1 | 0 |
| `apps/plugin/src/federated/nanofrontendTypes/libs/@splitsoftware/splitio-commons/splitio.d.ts` | 1 | 0 | 1 | 0 |
| `libs/backend-utils/src/config/fetchConfig.schema.ts` | 1 | 0 | 0 | 1 |
| `libs/backend-utils/src/middleware/gzipCompression.middleware.test.ts` | 1 | 0 | 0 | 1 |
| `libs/backend-utils/src/middleware/gzipCompression.middleware.ts` | 1 | 0 | 0 | 1 |
| `libs/backend-utils/src/middleware/loggerProfile.middleware.test.ts` | 1 | 0 | 0 | 1 |
| `libs/backend-utils/src/middleware/loggerProfile.middleware.ts` | 1 | 0 | 0 | 1 |

## Security Issues

**High:** 0 | **Medium:** 1 | **Low:** 3

| Severity | File | Line | Description |
|----------|------|------|-------------|
| MEDIUM | `apps/plugin/src/federated/nanofrontendTypes/libs/ag-grid/ag-grid-community/core/entities/gridOptions.d.ts` | 436 | Use of Function constructor |
| LOW | `apps/plugin/src/federated/nanofrontendTypes/libs/ag-grid/ag-charts-community/src/util/dom.d.ts` | 9 | Non-HTTPS URL (excluding localhost) |
| LOW | `apps/plugin/src/federated/nanofrontendTypes/libs/@splitsoftware/splitio-commons/splitio.d.ts` | 1557 | Non-HTTPS URL (excluding localhost) |
| LOW | `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.ts` | 204 | Non-HTTPS URL (excluding localhost) |

## Code Smells

| Type | Count |
|------|-------|
| Long Functions (>50 lines) | 1 |
| Deep Nesting (>4 levels) | 11 |
| Long Parameter Lists (>5) | 0 |
| Large Files (>300 LOC) | 3 |

### Top Offenders

| Type | File | Line | Details |
|------|------|------|---------|
| deep_nesting | `libs/backend-utils/src/config/fetchConfig.schema.ts` | 65 | Nesting depth reaches 5 levels |
| deep_nesting | `libs/backend-utils/src/middleware/gzipCompression.middleware.test.ts` | 56 | Nesting depth reaches 6 levels |
| deep_nesting | `libs/backend-utils/src/middleware/gzipCompression.middleware.ts` | 24 | Nesting depth reaches 5 levels |
| deep_nesting | `libs/backend-utils/src/middleware/loggerProfile.middleware.test.ts` | 51 | Nesting depth reaches 6 levels |
| deep_nesting | `libs/backend-utils/src/middleware/loggerProfile.middleware.ts` | 38 | Nesting depth reaches 6 levels |
| deep_nesting | `libs/backend-utils/src/middleware/requestValidation.middleware.test.ts` | 24 | Nesting depth reaches 5 levels |
| deep_nesting | `libs/backend-utils/src/database/docdb/docdb.session.test.ts` | 60 | Nesting depth reaches 5 levels |
| deep_nesting | `libs/backend-utils/src/database/utils/dataPoint/dataPoint.repository.test.ts` | 39 | Nesting depth reaches 5 levels |
| deep_nesting | `apps/plugin/webpack.config.ts` | 148 | Nesting depth reaches 7 levels |
| deep_nesting | `apps/api-core/src/config/loggerOptions.test.ts` | 11 | Nesting depth reaches 5 levels |
| deep_nesting | `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts` | 56 | Nesting depth reaches 9 levels |
| long_function | `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.ts` | 441 | Function 'getDataPointsBySource' is 68 lines |
| large_file | `plopfile.js` | 1 | File has 347 lines of code |
| large_file | `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts` | 1 | File has 1285 lines of code |
| large_file | `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.ts` | 1 | File has 456 lines of code |

## Duplicate Code

**50 duplicate groups** totaling 640 lines

| # | Lines | Locations |
|---|-------|-----------|
| 1 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:29`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:62`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:103` |
| 2 | 5 | `libs/backend-utils/src/testing-utils/dataset.fixtures.ts:8`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:423`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:661` |
| 3 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:28`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:61`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:815` |
| 4 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:31`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:64`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:348` |
| 5 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:32`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:65`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:349` |
| 6 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:33`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:66`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:350` |
| 7 | 5 | `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:30`, `libs/backend-utils/src/testing-utils/dataPoint.fixtures.ts:63`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:347` |
| 8 | 5 | `libs/backend-utils/src/testing-utils/dataset.fixtures.ts:7`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:422`, `apps/api-core/src/handlers/getDataPoints/getDataPoints.helper.test.ts:660` |
| 9 | 5 | `libs/backend-utils/src/database/utils/dataPoint/dataPoint.repository.test.ts:5`, `libs/backend-utils/src/database/utils/dataset/dataset.repository.test.ts:3`, `libs/backend-utils/src/database/utils/marketSegmentTabs/marketSegmentTabs.repository.test.ts:11` |
| 10 | 5 | `libs/backend-utils/src/database/utils/dataPoint/dataPoint.repository.test.ts:6`, `libs/backend-utils/src/database/utils/dataset/dataset.repository.test.ts:4`, `libs/backend-utils/src/database/utils/marketSegmentTabs/marketSegmentTabs.repository.test.ts:12` |

## Remediation Roadmap

1. **[medium]** Consolidate 50 duplicate code blocks (640 lines) — _+2 pts_
