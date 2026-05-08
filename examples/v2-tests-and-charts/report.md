# Code Scan Report

**Quality Score: 57/100 (Grade: F)**

---

## Summary

| Metric | Value |
|--------|-------|
| Path | `C:\Projects\mdc-excel-addin` |
| Total Files | 15,836 |
| Total Lines of Code | 454,239 |
| Functions Analyzed | 14,889 |
| Complex Functions (>10) | 682 |
| Security Issues | 168 |
| Code Smells | 904 |

## Languages

| Language | Files | Lines |
|----------|-------|-------|
| TypeScript | 14,867 | 111,445 |
| Other | 639 | 6,171 |
| JavaScript | 222 | 249,721 |
| HTML | 42 | 9,866 |
| JSON | 31 | 51,780 |
| Markdown | 18 | 1,410 |
| CSS | 17 | 23,846 |

## Top Complex Functions

| Function | File | Line | Complexity |
|----------|------|------|-----------|
| `getSelectorSpecificity` | `apps/plugin/src/federated/nanofrontendTestBundle/index-0KIrNK0y.js` | 951 | 9011 |
| `T` | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 104 | 4341 |
| `x` | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 164 | 1369 |
| `regexSafe` | `apps/plugin/src/federated/nanofrontendTestBundle/createTranslations-CJT7OseH.js` | 1060 | 611 |
| `createDOMPurify` | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 294 | 335 |
| `r` | `apps/plugin/src/federated/nanofrontendTestBundle/index-0KIrNK0y.js` | 460 | 233 |
| `naturalLogarithm` | `apps/plugin/src/federated/nanofrontendTestBundle/decimalValueFormatter-BDFSFJnB.js` | 3396 | 213 |
| `useAutocomplete` | `apps/plugin/src/federated/nanofrontendTestBundle/index-CRnKmCIH.js` | 3855 | 208 |
| `a` | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 145 | 199 |
| `k` | `apps/api-core/testing/reports/coverage/prettify.js` | 2 | 188 |

## Security Issues

**High:** 4 | **Medium:** 64 | **Low:** 100

| Severity | File | Line | Description |
|----------|------|------|-------------|
| HIGH | `libs/backend-utils/src/config/config.accessors.test.ts` | 21 | Possible hardcoded secret assigned to sensitive variable |
| HIGH | `libs/backend-utils/src/database/docdb/docdb.client.test.ts` | 18 | Possible hardcoded secret assigned to sensitive variable |
| HIGH | `libs/backend-utils/src/database/docdb/docdb.session.test.ts` | 47 | Possible hardcoded secret assigned to sensitive variable |
| HIGH | `libs/backend-utils/src/database/docdb/docdb.session.test.ts` | 96 | Possible hardcoded secret assigned to sensitive variable |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/AdapterDateFns-inC1JwCE.js` | 10438 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/AdapterDateFns-inC1JwCE.js` | 10617 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 105 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 127 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/Chart-tSNYgIac.js` | 164 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/clsx-Cwp20X_4.js` | 130 | Use of dangerouslySetInnerHTML |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 827 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 1405 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 1409 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 1428 | Direct innerHTML assignment |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 2417 | Use of dangerouslySetInnerHTML |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 2946 | Use of dangerouslySetInnerHTML |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/htmlSanitizer-BG2xV9Tp.js` | 4023 | Use of dangerouslySetInnerHTML |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/index-0KIrNK0y.js` | 6033 | Use of Function constructor |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/index-CRnKmCIH.js` | 317 | Use of dangerouslySetInnerHTML |
| MEDIUM | `apps/plugin/src/federated/nanofrontendTestBundle/index.esm-DqYj6TQe.js` | 7105 | Direct innerHTML assignment |

## Code Smells

| Type | Count |
|------|-------|
| Long Functions (>50 lines) | 578 |
| Deep Nesting (>4 levels) | 180 |
| Long Parameter Lists (>5) | 71 |
| Large Files (>300 LOC) | 75 |

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
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/AdapterDateFns-inC1JwCE.js` | 5449 | Nesting depth reaches 7 levels |
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/api-BglSbvNM.js` | 137 | Nesting depth reaches 5 levels |
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/appContextProviderGenerator-9_ibqJVL.js` | 42 | Nesting depth reaches 7 levels |
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/AutoClampTypography-CwHtWuiI.js` | 151 | Nesting depth reaches 6 levels |
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/AutoLayout-D6zBfX7s.js` | 505 | Nesting depth reaches 5 levels |
| deep_nesting | `apps/plugin/src/federated/nanofrontendTestBundle/ButtonBase-CXnvMMUo.js` | 492 | Nesting depth reaches 6 levels |
