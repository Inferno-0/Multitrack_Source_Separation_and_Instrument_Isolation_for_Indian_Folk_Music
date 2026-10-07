# DATASET STANDARDIZATION REPORT

**Date/Time:** 2026-08-25 23:44:47.439231
**Source Dataset Path:** `D:\ISOLATED_INSTRUMENTS`
**Output Dataset Path:** `D:\ISOLATED_INSTRUMENTS_PREPARED`

## 1. Global Accounting
- Total Source Files Expected: 2476
- Total Files Successfully Standardized: 2476
- Total Conversion Failures: 0
- Total Files Requiring Resampling: 1550
- Total Files Requiring Downmixing: 657
- Total Files Requiring Both: 27
- Manual Review Files Preserved: 1

## 2. Dholak Sample 26 Status
Successfully detected, processed, and explicitly marked with `signal_quality_status = EXTREMELY_SHORT_ACTIVE_SIGNAL` and `curation_status = MANUAL_REVIEW` in `dholak/metadata.csv`.

## 3. Four Newly Added Dhul Files
Included successfully as part of the 13 total Dhul files verified in the audit.

## 4. Per-Instrument Statistics
### Vocals
- **File Count:** Expected 160 / Actual 160
- **Original Duration:** 34.1222 hours
- **Standardized Duration:** 34.1222 hours
- **Original Sample Rates:** {44100}
- **Original Channels:** {1}
- **Resampled:** 0 | **Downmixed:** 0

### Tabla
- **File Count:** Expected 797 / Actual 797
- **Original Duration:** 2.5386 hours
- **Standardized Duration:** 2.5386 hours
- **Original Sample Rates:** {16000, 44100}
- **Original Channels:** {1, 2}
- **Resampled:** 236 | **Downmixed:** 561

### Harmonium
- **File Count:** Expected 1322 / Actual 1322
- **Original Duration:** 1.3096 hours
- **Standardized Duration:** 1.3096 hours
- **Original Sample Rates:** {48000, 22050, 44100}
- **Original Channels:** {1, 2}
- **Resampled:** 1315 | **Downmixed:** 8

### Flute
- **File Count:** Expected 129 / Actual 129
- **Original Duration:** 0.7954 hours
- **Standardized Duration:** 0.7954 hours
- **Original Sample Rates:** {48000, 44100}
- **Original Channels:** {1, 2}
- **Resampled:** 17 | **Downmixed:** 47

### Dhul
- **File Count:** Expected 13 / Actual 13
- **Original Duration:** 0.3045 hours
- **Standardized Duration:** 0.3045 hours
- **Original Sample Rates:** {48000, 44100}
- **Original Channels:** {2}
- **Resampled:** 9 | **Downmixed:** 13

### Dholak
- **File Count:** Expected 55 / Actual 55
- **Original Duration:** 0.0914 hours
- **Standardized Duration:** 0.0914 hours
- **Original Sample Rates:** {44100}
- **Original Channels:** {2}
- **Resampled:** 0 | **Downmixed:** 55

## 5. Integrity and Provenance
- Complete one-to-one provenance maintained.
- Original SHA-256 and Standardized SHA-256 recorded in per-instrument metadata.
- Original dataset left strictly untouched.

## 6. Final Status
**PASS**: Standardization completed flawlessly with 0 failures.