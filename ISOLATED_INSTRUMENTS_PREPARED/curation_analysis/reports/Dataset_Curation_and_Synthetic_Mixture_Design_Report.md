# Dataset Curation and Synthetic Mixture Design Report

## 1. Purpose
This report provides a comprehensive, read-only analysis of the standardized isolated-instrument dataset located at `D:\ISOLATED_INSTRUMENTS_PREPARED`. It establishes duration statistics, explores the severe data imbalance, analyzes candidate training segment lengths, and proposes a data leakage-safe methodology for synthetic mixture generation for the query-based instrument separation model. No audio has been modified, generated, or deleted.

## 2. Dataset Inventory
Based on `D:\ISOLATED_INSTRUMENTS_PREPARED`:
- **Total Files:** 2476
- **Total Duration:** 39.16 hours

### Summary per Source:
| Instrument   |   Files |   Total_Duration_h |   Percentage_of_Total_Duration |
|:-------------|--------:|-------------------:|-------------------------------:|
| Vocals       |     160 |         34.1222    |                      87.1316   |
| Tabla        |     797 |          2.53858   |                       6.48231  |
| Harmonium    |    1322 |          1.30961   |                       3.34412  |
| Flute        |     129 |          0.79535   |                       2.03094  |
| Dholak       |      55 |          0.0914213 |                       0.233446 |
| Dhul         |      13 |          0.304524  |                       0.777608 |

## 3. Standardization Verification
All analyzed metadata rows correspond to audio files that were standardized strictly to:
- **44.1 kHz**
- **Mono (1 Channel)**
- **16-bit PCM WAV**
The authoritative source directory (`D:\ISOLATED_INSTRUMENTS`) remains strictly untouched, and all durations were preserved perfectly.

## 4. Duration Analysis
The dataset exhibits extreme imbalance in both total mass and clip distribution:
- **Vocals** dominate with ~87% of the total dataset duration. Vocal clips are generally full songs or long stems (median ~409s).
- **Harmonium** has 1,322 files but represents only ~3.3% of the duration, with an extremely short median duration (3.0s).
- **Tabla, Dhul, and Dholak** are heavily weighted toward short percussive hits or short loops (medians between 6s and 14s). 

## 5. Short-Clip Analysis
While conventional models drop audio shorter than a defined segment length (e.g., 10s), removing files < 5s would discard over 60% of the Harmonium and Tabla clips. Because instrument separation must capture transients and short percussive hits, these short files **should not be deleted**. 
- **Recommendation:** Retain clips between 1s and 5s as `KEEP_SHORT_EVENT`. During synthetic mixing, these can be padded with zeros or tiled/repeated to fill the mixture window, realistically mimicking sparse percussive hits or staccato phrasing. Clips under 1s are generally too short to provide reliable harmonic or temporal context and could be excluded to prevent artifacts, except where manually overridden.

## 6. Dholak Sample 26
- **Original Filename:** Dholak Sample - 26.wav
- **Duration:** 6.90s
- **Status:** Evaluated as having an extremely short active signal with a high silence ratio. However, as requested, it is tagged for `MANUAL_REVIEW` and not deleted. It could be retained specifically for transient event injection but should be excluded from continuous accompaniment mixing.

## 7. Dhul Dataset
The 4 newly added Dhul files are verified present, bringing the total to 13 files (approx. 0.30 hours). They have been incorporated into the duration statistics and plots.

## 8. Source Balance
The severe imbalance (Vocals = 34h, Dholak = 0.09h) implies that random sampling across the dataset will result in models that virtually never see Dholak or Dhul. 
- **Implication:** The synthetic mixture generator *must* employ forced balanced source sampling. We must oversample minority classes (Dholak, Dhul, Flute) and drastically undersample Vocals. If a mixture requires 3 instruments, the generator should pick instruments uniformly, then sample clips uniformly from those instruments. 

## 9. Candidate Segment Lengths
Number of independent segments available without repetition:
| Instrument   |   Independent_Segments_5s |   Independent_Segments_10s |   Independent_Segments_20s |
|:-------------|--------------------------:|---------------------------:|---------------------------:|
| Vocals       |                     24492 |                      12209 |                       6069 |
| Tabla        |                      1433 |                        517 |                        168 |
| Harmonium    |                       151 |                         73 |                         35 |
| Flute        |                       507 |                        214 |                         79 |
| Dholak       |                        39 |                          6 |                          0 |
| Dhul         |                       211 |                        103 |                         47 |
- **Finding:** A 10s or 20s segment length severely restricts Dholak and Harmonium (almost 0 independent 20s segments). A **5s to 10s** segment length is highly recommended to maximize the diversity of clips that can be sampled without heavy repetition padding. 

## 10. Proposed File Curation Policy
- **KEEP_NORMAL:** Files >= 5.0 seconds. Suitable for continuous mixture material.
- **KEEP_SHORT_EVENT:** Files between 1.0s and 5.0s. Suitable for tiling, zero-padding, or transient injection.
- **MANUAL_REVIEW:** Dholak 26 and any other anomalous signals.
- **EXCLUDE:** Files < 1.0s (excluding overrides).

## 11. Proposed Train/Validation/Test Split
To prevent data leakage, the split **must** be performed at the *original file level* before any cropping or mixing occurs. 
- **Strategy:** Assign each of the 2,476 standardized WAV files to a Split ID (e.g., 80% Train, 10% Val, 10% Test). The synthetic mixture generator will only mix files that share the same Split ID. 
- **Caution:** For severely data-poor classes (Dholak: 55 files, Dhul: 13 files), a strict 10% test split means only 1 or 5 files for testing. We may need a custom split ratio (e.g., reserve a fixed N files for test) for minority classes.

## 12. Synthetic Mixture Configurations
- **1 Instrument + Vocals:** Baseline query task. High diversity possible.
- **2-3 Instruments + Vocals:** Ideal for polyphonic separation robustness. The bottleneck will be pairing minority classes without repeating them too often.
- **4-6 Instruments:** Very high risk of overfitting to the limited combinations of Dhul and Dholak. Reserve for validation/stress-testing rather than heavy training. 

## 13. `Other` Strategy
To create a meaningful `other` class (instruments present in the mix but not queried), the mixture generator can randomly assign one of the 6 known instruments as `other` during an epoch, effectively teaching the model to ignore it. However, to truly generalize, a separate dataset of entirely unmodeled instruments (e.g., Guitar, Piano, Synth) should be introduced purely as "distractor" noise stems.

## 14. Provenance Metadata Schema
Proposed future mixture JSON schema:
```json
{
  "mixture_id": "mix_0001",
  "split": "train",
  "segment_length": 10.0,
  "sample_rate": 44100,
  "sources": [
    {
      "instrument": "tabla",
      "source_file": "tabla_000042.wav",
      "start_time_in_source": 12.5,
      "duration_used": 10.0,
      "gain_db": -3.0
    },
    {
      "instrument": "vocals",
      "source_file": "vocals_000105.wav",
      "start_time_in_source": 45.0,
      "duration_used": 10.0,
      "gain_db": -1.5
    }
  ]
}
```

## 15. Final Recommendation
1. Authorize the assignment of the Train/Val/Test Split tags into the metadata CSVs.
2. Adopt a 5s or 10s synthetic segment length.
3. Construct the Synthetic Mixture Generator using a balanced instrument sampling approach (oversampling minority classes and repeating short events).
4. No audio files should be deleted.
