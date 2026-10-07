# Current State Verification Report

**Date:** 2026-08-26
**Target Pipeline:** Stage 5 - Instrument Separation

---

## 1. Directory and File Checks

- **Original Dataset:** `D:\ISOLATED_INSTRUMENTS` exists and is fully readable. No modifications were performed.
- **Prepared Dataset:** `D:\ISOLATED_INSTRUMENTS_PREPARED` exists and contains the expected class folders: `vocals`, `tabla`, `harmonium`, `flute`, `dholak`, `dhul`.

## 2. Audio File Integrity and Properties

- **Format Validated:** 16-bit PCM WAV.
- **Channels Validated:** Mono (1 Channel).
- **Sample Rate Validated:** 44,100 Hz.
- **Audio Integrity:** All sampled files are finite and contain no NaN/Inf values.

## 3. Class Counts and Provenance

- **Vocals:** 160 WAV files, 160 metadata rows
- **Tabla:** 797 WAV files, 797 metadata rows
- **Harmonium:** 1322 WAV files, 1322 metadata rows
- **Flute:** 129 WAV files, 129 metadata rows
- **Dholak:** 55 WAV files, 55 metadata rows
- **Dhul:** 13 WAV files, 13 metadata rows

**Specific Validations:**
- **Dholak Sample 26:** Confirmed present and correctly flagged with `curation_status: MANUAL_REVIEW` due to extreme brevity.
- **Dhul Recordings:** Confirmed present (13 source recordings).

## 4. Checkpoints

- **HT-Demucs Initial 2-Stem Checkpoint:** `D:\finetune_htdemucs_runs\init_2stem_model.pt` (Exists)
- **HT-Demucs Fine-Tuned Checkpoint:** `D:\finetune_htdemucs_runs\run_002\best.pt` (Exists)
- **Banquet Pretrained Checkpoint:** `C:\iks_scripts\query-bandit\ev-pre-aug.ckpt` (Exists)

**Conclusion:** The project state is frozen, verified, and correctly standardized. The authoritative data remains unmodified.
