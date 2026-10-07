# ISOLATED INSTRUMENTS Dataset Audit Report

## 1. Directory Inspected
`G:\My Drive\IKS_Music_Source_Separation_and_Instrument_Isolation\03_Datasets\ISOLATED_INSTRUMENTS`

## 2. Datasets Discovered
The following top-level datasets were identified:
- Flute
- Dhul
- Harmonium
- Dholak
- Tabla
- Vocals

## 3. Instruments/Sources Represented
Inferred from dataset folder names:
- flute
- dhul
- harmonium
- dholak
- tabla
- vocals

## 4. Number of files per dataset
- **Flute**: 231 files (129 valid audio files)
- **Dhul**: 9 files (9 valid audio files)
- **Harmonium**: 1322 files (1322 valid audio files)
- **Dholak**: 55 files (55 valid audio files)
- **Tabla**: 1741 files (797 valid audio files)
- **Vocals**: 162 files (162 valid audio files)

## 5. Total duration
**Total Usable Duration**: 40.41 hours across all datasets.
- **Flute**: 0.80 hours
- **Dhul**: 0.03 hours
- **Harmonium**: 1.31 hours
- **Dholak**: 0.09 hours
- **Tabla**: 2.54 hours
- **Vocals**: 35.65 hours

## 6. Duration distributions
Counts of audio files within specific duration buckets:
| Dataset | < 1s | 1-3s | 3-5s | 5-10s | 10-30s | 30-60s | 1-5m | > 5m |
|---|---|---|---|---|---|---|---|---|
| Flute | 0 | 0 | 2 | 32 | 62 | 32 | 1 | 0 |
| Dhul | 0 | 0 | 0 | 2 | 7 | 0 | 0 | 0 |
| Harmonium | 0 | 0 | 1314 | 1 | 1 | 1 | 4 | 1 |
| Dholak | 0 | 2 | 20 | 27 | 6 | 0 | 0 | 0 |
| Tabla | 0 | 95 | 164 | 319 | 178 | 19 | 22 | 0 |
| Vocals | 0 | 0 | 0 | 0 | 0 | 4 | 42 | 116 |

## 7. Sample-rate distributions
- **Flute**: 44100Hz (112), 48000Hz (17)
- **Dhul**: 48000Hz (9)
- **Harmonium**: 44100Hz (7), 48000Hz (1), 22050Hz (1314)
- **Dholak**: 44100Hz (55)
- **Tabla**: 44100Hz (561), 16000Hz (236)
- **Vocals**: 44100Hz (162)

## 8. Channel distributions
- **Flute**: 2ch (47), 1ch (82)
- **Dhul**: 2ch (9)
- **Harmonium**: 2ch (8), 1ch (1314)
- **Dholak**: 2ch (55)
- **Tabla**: 2ch (561), 1ch (236)
- **Vocals**: 1ch (162)

## 9. File-format distributions
- **Flute**: .wav (129)
- **Dhul**: .wav (9)
- **Harmonium**: .wav (1322)
- **Dholak**: .wav (55)
- **Tabla**: .wav (797)
- **Vocals**: .wav (162)

## 10. Isolation status
Based on directory and filename heuristics:
- **Flute**: 129 isolated, 0 mixed, 0 unknown
- **Dhul**: 9 isolated, 0 mixed, 0 unknown
- **Harmonium**: 1322 isolated, 0 mixed, 0 unknown
- **Dholak**: 55 isolated, 0 mixed, 0 unknown
- **Tabla**: 797 isolated, 0 mixed, 0 unknown
- **Vocals**: 162 isolated, 0 mixed, 0 unknown

## 11. Mixed/contaminated recordings
Detected **0** files with filenames/paths suggesting mixed audio (e.g. contains 'mix', 'bg', 'accompaniment').

## 12. Corrupt/unreadable files
Detected **0** corrupt or unreadable audio files.

## 13. Silent/near-silent files
Detected **1** files that are fully or nearly silent (based on RMS thresholds).

## 14. Very short files
Detected **0** files under 1.0 second duration.

## 15. Dataset imbalance
Comparing datasets by usable duration:
- **Vocals**: 35.65 hrs (Median dur: 422.09s)
- **Tabla**: 2.54 hrs (Median dur: 6.58s)
- **Harmonium**: 1.31 hrs (Median dur: 3.00s)
- **Flute**: 0.80 hrs (Median dur: 19.43s)
- **Dholak**: 0.09 hrs (Median dur: 6.03s)
- **Dhul**: 0.03 hrs (Median dur: 13.50s)
The Vocals dataset often heavily outweighs individual instruments, which must be addressed during synthetic mixture generation.

## 16. Metadata/annotation differences
Documents found per dataset:
- **Flute**: 1 metadata files found (e.g., Flute\Kaggle_Classification_Clips\Flute\dataset.csv)
- **Dhul**: No metadata files found.
- **Harmonium**: No metadata files found.
- **Dholak**: No metadata files found.
- **Tabla**: No metadata files found.
- **Vocals**: No metadata files found.

## 17. Files requiring manual review
**1** files require manual review (see `problematic_files.csv`).

## 18. Recommended standardization strategy
- Target: **44100 Hz, Mono or Stereo WAV**.
- Action: Resample all non-44.1kHz files. Convert FLAC/MP3/M4A to WAV for training efficiency.
- Filtering: Ignore/remove files under 1.0s or completely silent files.

## 19. Recommended retention strategy
- Retain all clean, isolated audio > 1.0s.
- Set aside `mixed` tracks for validation, or discard them from synthetic training to prevent leakage.

## 20. Recommended deletion candidates
No files have been deleted. However, candidates for exclusion from the final training set include:
- 0 corrupt files.
- 1 silent/near-silent files.
- 0 files under 1.0 second.

---
## Recommended Dataset Preparation Plan

### Flute
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.

### Dhul
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.

### Harmonium
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.

### Dholak
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.

### Tabla
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.

### Vocals
- **KEEP**: All valid audio files > 1.0s.
- **CONVERT/RESAMPLE**: All non-WAV and non-44100Hz audio must be standardized.
- **REVIEW**: Files flagged as SILENT or NEAR_SILENT.
- **EXCLUDE**: Corrupt files and files under 1.0s.
