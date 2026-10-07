# ISOLATED INSTRUMENTS Audit Report v2

## 1. Executive Summary
Complete read-only forensic audit performed. No source files modified.
- Total Audio Files: 2476
- Total Usable Duration: 39.16 hours
- Exact Duplicates: 0 files

## 2. Dataset Location
`D:\ISOLATED_INSTRUMENTS`

## 3. Per-Instrument Statistics
### Vocals
- Files: 160
- Hours:  34.1222 (87.1% of total dataset)
- Median Dur: 409.46s
- Sample Rates: {44100: 160}
- Channels: {1: 160}

### Tabla
- Files: 797
- Hours:  2.5386 (6.5% of total dataset)
- Median Dur: 6.58s
- Sample Rates: {44100: 561, 16000: 236}
- Channels: {2: 561, 1: 236}

### Harmonium
- Files: 1322
- Hours:  1.3096 (3.3% of total dataset)
- Median Dur: 3.00s
- Sample Rates: {22050: 1314, 44100: 7, 48000: 1}
- Channels: {1: 1314, 2: 8}

### Flute
- Files: 129
- Hours:  0.7954 (2.0% of total dataset)
- Median Dur: 19.43s
- Sample Rates: {44100: 112, 48000: 17}
- Channels: {2: 47, 1: 82}

### Dhul
- Files: 13
- Hours:  0.3045 (0.8% of total dataset)
- Median Dur: 14.00s
- Sample Rates: {44100: 4, 48000: 9}
- Channels: {2: 13}

### Dholak
- Files: 55
- Hours:  0.0914 (0.2% of total dataset)
- Median Dur: 6.03s
- Sample Rates: {44100: 55}
- Channels: {2: 55}

## 4. Duration Distribution
| Dataset | < 1s | 1-2s | 2-5s | 5-10s | 10-30s | 30+s |
|---|---|---|---|---|---|---|
| Dholak | 0 | 0 | 22 | 27 | 6 | 0 |
| Dhul | 0 | 0 | 0 | 2 | 9 | 2 |
| Flute | 0 | 0 | 2 | 32 | 62 | 33 |
| Harmonium | 0 | 0 | 1314 | 1 | 1 | 6 |
| Tabla | 0 | 23 | 236 | 319 | 178 | 41 |
| Vocals | 0 | 0 | 0 | 0 | 0 | 160 |

## 5. Dholak Sample 26 Analysis
Manually checked by user previously. Automatically flagged during this audit due to low overall RMS / high near-silence fraction. However, per instructions, it is explicitly classified as `EXTREMELY_SHORT_ACTIVE_SIGNAL` and recommended for `MANUAL_REVIEW` rather than outright exclusion.

## 6. Newly Added Dhul Files
The 4 newly added Dhul files were detected and verified:
- `Assamese  Bihu Dhol (Copyright free).wav`: SR=44100, Ch=2, Dur=229.33s, Size=40556964 bytes
- `Assamese Bihu Dhol Recording Session.wav`: SR=44100, Ch=2, Dur=15.03s, Size=2718672 bytes
- `Bihu Rhythm Loop _ Indian Pattern.wav`: SR=44100, Ch=2, Dur=721.95s, Size=127463416 bytes
- `dhul badan__dholbadan__dhol badan__bihu 2025__bihu dhol__bihu dhul__Assamese bihu dhol__bihu.wav`: SR=44100, Ch=2, Dur=12.64s, Size=2323322 bytes
- `Gully-Loops-Bhoral-Dhul-Loop-BPM-160.wav`: SR=48000, Ch=2, Dur=12.00s, Size=3456044 bytes
- `Gully-Loops-Bordoisila-Dhul-Loop-BPM-120.wav`: SR=48000, Ch=2, Dur=12.00s, Size=3456044 bytes
- `Gully-Loops-Dhemaji-Dhul-Loop.wav`: SR=48000, Ch=2, Dur=9.62s, Size=2770244 bytes
- `Gully-Loops-Dhumuha-Dhul-Loop-BPM-100.wav`: SR=48000, Ch=2, Dur=14.40s, Size=4147244 bytes
- `Gully-Loops-Jhumor-Dhul-Loop-BPM-120.wav`: SR=48000, Ch=2, Dur=18.00s, Size=5184044 bytes
- `Gully-Loops-Kopou-Loop-BPM-140.wav`: SR=48000, Ch=2, Dur=13.50s, Size=3888044 bytes
- `Gully-Loops-Mahor-Dhul-Loop-BPM-120.wav`: SR=48000, Ch=2, Dur=14.00s, Size=4032044 bytes
- `Gully-Loops-Nahor-Dhul-Loop.wav`: SR=48000, Ch=2, Dur=14.20s, Size=4090544 bytes
- `Gully-Loops-Rohedoi-Dhul-Loop-BPM-100.wav`: SR=48000, Ch=2, Dur=9.60s, Size=2764844 bytes
Total Dhul files is now 13.

## 7. Recommended Curation Decisions
Based on objective metrics and rules, the following actions are recommended:
- **KEEP**: 898
- **KEEP_AFTER_RESAMPLING**: 1577
- **EXCLUDE_FROM_TRAINING**: 0
- **MANUAL_REVIEW**: 1

## 8. Dataset Standardization Design & Metadata Schema

### Proposed Logical Structure
`D:\ISOLATED_INSTRUMENTS_PREPARED\`
- `vocals/audio/`, `vocals/metadata.csv`
- `tabla/audio/`, `tabla/metadata.csv`
- etc.

### Metadata Schema
- `standardized_filename`, `original_filename`, `instrument`, `source_dataset`
- `original_path`, `original_sample_rate`, `standardized_sample_rate`
- `original_channels`, `standardized_channels`, `original_duration_seconds`, `standardized_duration_seconds`
- `original_num_samples`, `standardized_num_samples`, `original_format`, `original_file_size`
- `original_sha256`, `standardized_sha256`, `rms_level`, `signal_quality_status`, `curation_status`
- `exclusion_reason`, `processing_applied`, `notes`

## 9. Synthetic Mixture Readiness
1. **Data Imbalance**: Vocals heavily dominate. Dhul & Dholak are severely data-poor.
2. **Oversampling Needs**: Dhul and Dholak will require extreme oversampling or augmentation to be represented robustly.
3. **Crop Lengths**: With many 1-3s tracks in Tabla/Dhul/Dholak, the synthetic crop length cannot exceed 2.0s or 3.0s unless short percussive hits are padded with silence.
4. **Standardization**: Files are currently disjoint in sample rate (44.1k, 48k, 22.05k, 16k). Standardizing to 44.1k is highly recommended.
5. **Channel Policy**: Given that these are isolated sources, converting all to Mono is technically justifiable and simplifies mixing, unless spatialization is explicitly desired in the mixtures. Recommend standardizing to Mono.