# Experiment Overview
EXP002 assesses the performance of the pretrained HT-Demucs model on multiple Indian folk music recordings. It serves to validate the consistency of the source separation baseline established in EXP001 across an expanded dataset.

# Objective
Evaluate the consistency of HT-Demucs source separation across multiple recordings of the same folk tradition using the exact same experimental configuration as EXP001.

# Hypothesis
The pretrained HT-Demucs model will successfully separate vocals from accompaniment but will not reliably isolate individual Indian folk instruments because it was trained on broad Western source categories.

# Dataset
BIHU (10 recordings)

# Model
HT-Demucs (Pretrained)

# Experimental Setup
Baseline two-stem (vocals/accompaniment) source separation using HT-Demucs. Processing all available audio recordings in the selected folk tradition directory.

# Methodology
1. **Repository preparation**: The experiment environment and directory structure were initialized.
2. **Input recordings**: The dataset directory was scanned for the 10 target audio files.
3. **HTDemucs execution**: Batch inference was executed across the recordings using the pretrained model.
4. **Output organization**: The generated stems were appropriately renamed and stored in the outputs directory.
5. **Validation**: Execution logs and successful file generation were verified.
6. **Manual qualitative evaluation**: A listening evaluation was conducted to assess the separation quality.

# Execution Summary
The experiment successfully performed two-stem separation on 10 BIHU folk recordings. Execution completed smoothly with separated vocal and accompaniment stems cleanly generated and logged for each input track.

# Output Structure
```text
05_Experiments/Baseline_HT_Demucs/EXP002/
├── logs/
│   └── execution_log.txt
├── notebook/
│   └── EXP002_HTDemucs_Baseline.ipynb
└── outputs/
    └── htdemucs/
```

# Documentation
- **observations.md**: Factual qualitative observations obtained from manual listening evaluation.
- **conclusions.md**: Research interpretations, implications, and future directions.
- **execution log**: Technical execution details maintained within the `logs/` directory.

# Key Findings
- Reliable vocal separation
- Accompaniment preservation
- Flute leakage
- Low artifacts
- Qualitative baseline established

# Known Limitations
- Flute leakage into the vocal stem.
- Secondary vocal leakage.
- Occasional percussion leakage.
- One outlier recording with lower quality.

# Future Work
- Fine-tuning HTDemucs on Indian folk music.
- Reducing leakage.
- Extending separation toward selected primary folk instruments.

# Repository Notes
Detailed song-by-song qualitative observations are maintained in the physical laboratory notebook. The repository documentation summarizes the overall experimental findings.
