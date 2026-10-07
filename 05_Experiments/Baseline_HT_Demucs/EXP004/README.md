# EXP004 - Baseline HT-Demucs Evaluation on Pandavani

## Overview
EXP004 evaluates the baseline HT-Demucs model on five Pandavani recordings using two-stem vocal/accompaniment separation, employing the finalized physical chunking and reconstruction production pipeline.

## Objective
To evaluate the qualitative baseline capabilities of HT-Demucs source separation on the Pandavani folk tradition across recordings of varying lengths using a standardized physical chunking and reconstruction architecture.

## Dataset
- **Tradition:** Pandavani
- **Recordings:** 5
- **Files:** PNDV_009, PNDV_012, PNDV_018, PNDV_021, PNDV_024

## Model
- **Model:** HT-Demucs
- **Architecture version:** htdemucs

## Experimental Setup
The experiment was executed using CUDA with sequential processing. The task consisted of two-stem separation producing distinct `Vocals` and `No-Vocals` (accompaniment) outputs for each input recording.

## Physical Chunking and Reconstruction
EXP004 utilized the established production pipeline in which every recording is physically chunked before HT-Demucs inference with the following configuration:
- **Physical chunk duration:** 60 seconds
- **Overlap:** 5 seconds
- **Step:** 55 seconds
- **Demucs internal segment:** 7 seconds

Following HT-Demucs separation, the Vocals and No-Vocals chunk outputs were reconstructed into full-length recordings using an overlap-based crossfade procedure, preserving the exact original recording durations.

## Output Structure
```text
outputs/
├── PNDV_009/
│   ├── PNDV_009_Vocals.wav
│   └── PNDV_009_No_Vocals.wav
├── PNDV_012/
│   ├── PNDV_012_Vocals.wav
│   └── PNDV_012_No_Vocals.wav
├── PNDV_018/
│   ├── PNDV_018_Vocals.wav
│   └── PNDV_018_No_Vocals.wav
├── PNDV_021/
│   ├── PNDV_021_Vocals.wav
│   └── PNDV_021_No_Vocals.wav
└── PNDV_024/
    ├── PNDV_024_Vocals.wav
    └── PNDV_024_No_Vocals.wav
```

## Validation
- 10 expected output files were generated.
- All 10 expected WAV files were present in recording-specific directories.
- All 10 outputs were readable.
- All 10 outputs passed audio integrity validation (44.1 kHz, stereo, valid audio frames).
- The pipeline confirmed that the reconstructed outputs perfectly preserve the original recording durations.

## Qualitative Findings
Manual qualitative listening revealed highly consistent behavior across all five recordings:
- Vocal separation was consistently clean and acceptable with only minor non-vocal remnants in the Vocals outputs.
- No noticeable vocal leakage was heard in the No-Vocals outputs.
- The accompaniment remained usable and intact.
- No audible chunk-boundary or reconstruction artifacts were identified.

## Conclusion
Within the five-recording qualitative sample evaluated, baseline HT-Demucs produced consistent and usable two-stem separation for Pandavani recordings. Vocal outputs were generally clean and natural, while the No-Vocals outputs retained the accompaniment without noticeable vocal leakage. The successful execution of the physical chunking, overlap, and reconstruction pipeline demonstrated that the established processing architecture successfully handled the tested recordings of various durations while preserving the original recording length. However, this result is limited to qualitative listening on five recordings and does not establish quantitative separation performance or guarantee universal generalization.

## Evaluation Status
- **Subjective evaluation:** Completed
- **Objective evaluation:** Pending (Quantitative metrics have not been calculated)

## Related Files
- `notebook/EXP004_HTDemucs_Baseline.ipynb`
- `logs/execution_log.json`
- `observations.md`
- `conclusions.md`
- `config.yaml`
- `outputs/`
- `chunked_processing/`
