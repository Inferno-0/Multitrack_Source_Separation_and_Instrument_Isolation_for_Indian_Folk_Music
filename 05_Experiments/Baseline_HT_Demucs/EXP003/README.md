# EXP003 - Baseline HT-Demucs Evaluation on Baul Geet

## Overview
EXP003 evaluates the baseline HT-Demucs model on three Baul Geet recordings using two-stem vocal/accompaniment separation.

## Objective
To evaluate the performance of the HT-Demucs source separation model on the curated Baul Geet folk music dataset by separating each recording into two stems, Vocals and No-Vocals (Accompaniment), and to qualitatively assess the separation performance through manual listening.

## Dataset
- Baul Geet
- 3 recordings
- BAUL_002
- BAUL_016
- BAUL_024

## Model
- HT-Demucs
- htdemucs

## Experimental Setup
The experiment was executed via Google Colab utilizing a Tesla T4 GPU. The task consisted of two-stem separation producing distinct `Vocals` and `No-Vocals` (accompaniment) outputs for each input recording.

## Output Structure
```text
outputs/
├── BAUL_002/
│   ├── BAUL_002_Vocals.wav
│   └── BAUL_002_No_Vocals.wav
├── BAUL_016/
│   ├── BAUL_016_Vocals.wav
│   └── BAUL_016_No_Vocals.wav
└── BAUL_024/
    ├── BAUL_024_Vocals.wav
    └── BAUL_024_No_Vocals.wav
```

## Validation
- 6 output files were generated.
- All expected files were present.
- All outputs were readable.
- All outputs passed audio integrity validation.
- The outputs were 44.1 kHz stereo according to the validation results.

## Qualitative Findings
- **BAUL_002:** Clean separation with no noticeable vocal or instrument leakage.
- **BAUL_016:** Significant and complete Ektara leakage into Vocals, while other aspects remained good.
- **BAUL_024:** Clean separation with no noticeable vocal or instrument leakage.

## Conclusion
Within the three-recording qualitative sample evaluated in EXP003, HT-Demucs produced generally clean and usable two-stem separation of vocals and accompaniment for Baul Geet. BAUL_002 and BAUL_024 showed no noticeable vocal or instrument leakage, while BAUL_016 exhibited prominent Ektara leakage into the Vocals output. Therefore, although the baseline performed well overall in this limited sample, instrument-specific leakage remains a notable limitation.

## Evaluation Status
- Subjective evaluation: completed
- Objective evaluation: pending

Future objective evaluation will use SDR, SI-SDR, SIR and SAR.

## Related Files
- `notebook/EXP003_HTDemucs_Baseline.ipynb`
- `logs/execution_log.txt`
- `observations.md`
- `conclusions.md`
- `config.yaml`
- `outputs/`
