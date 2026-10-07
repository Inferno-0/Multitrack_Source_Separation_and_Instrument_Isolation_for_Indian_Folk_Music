# Leakage-Safe Source Splits Report

**Date:** 2026-08-26

## 1. Split Methodology
The dataset was split into `TRAIN`, `VALIDATION`, and `TEST` at the **Original Recording Level**. 
- The provenance field `original_filename` was used to ensure all cropped segments of the same original recording fall strictly into the same split.
- Dholak Sample 26 was hardcoded to `EXCLUDED` and will not be selected as a mixture or query source.
- Vocals are assigned `eligible_as_query_source = False` since they are not a target class.

## 2. Split Results by Instrument

| Instrument | Train | Validation | Test | Excluded |
| --- | --- | --- | --- | --- |
| Vocals | 112 | 24 | 24 | 0 |
| Tabla | 559 | 119 | 119 | 0 |
| Harmonium | 926 | 198 | 198 | 0 |
| Flute | 94 | 17 | 18 | 0 |
| Dholak | 39 | 7 | 8 | 1 |
| Dhul | 11 | 1 | 1 | 0 |

**Overall Breakdown:**
- **TRAIN:** 1,741 files
- **VALIDATION:** 366 files
- **TEST:** 368 files
- **EXCLUDED:** 1 file

## 3. Query and Mixture Roles
In order to preserve the pool size for minority classes (Dhul/Dholak), files are generically flagged as `eligible_as_mixture_source` and `eligible_as_query_source`. 
**Crucial Rule:** The synthetic mixture generator is strictly programmed to prevent selecting the same original recording for both the mixture and the query *within the same synthetic example*. 

## 4. Manifest Location
- CSV: `D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv`
- JSON: `D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.json`
