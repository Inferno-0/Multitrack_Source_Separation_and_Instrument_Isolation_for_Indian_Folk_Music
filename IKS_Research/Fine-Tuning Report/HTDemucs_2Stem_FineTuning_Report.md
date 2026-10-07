# HT-Demucs 2-Stem Fine-Tuning Report

**Project:** IKS Music Source Separation and Instrument Isolation  
**Stage:** 2-Stem Fine-Tuning (Completed)  
**Report Date:** 2026-08-24  
**Report Status:** Final

---

## 1. Overview

This document is the formal technical record of the HT-Demucs 2-stem fine-tuning stage of the IKS Music Source Separation and Instrument Isolation project. The goal of this stage was to adapt the publicly pretrained HT-Demucs 4-stem model to the specific acoustic characteristics of Carnatic and Indian folk music recordings from the Saraga dataset, operating in a 2-stem (vocals vs. accompaniment) configuration.

The fine-tuning process has been completed. The resulting fine-tuned HT-Demucs model is the artifact that will carry forward into the next stage: objective source-separation evaluation using standard metrics (SDR, SI-SDR, SIR, SAR).

---

## 2. Objective of Fine-Tuning

The pretrained HT-Demucs model was originally trained on MUSDB18, a dataset of Western popular music. Indian classical and folk recordings differ substantially in:

- tonal structure and melodic vocabulary (raga-based, microtonal)
- rhythmic character (tala-based, with instruments such as tabla and mridangam)
- vocal style and ornamentation (meend, gamaka)
- instrumentation (no standard Western rhythm section)

Fine-tuning on domain-specific recordings was performed to shift the model's learned representation toward this acoustic domain, with the expectation that a domain-adapted model would produce better separation quality on Indian music than a model applied zero-shot.

The fine-tuning task is defined as:

```
Mixture audio -> Vocals + Accompaniment
```

This is a 2-stem formulation. Individual-instrument separation (e.g., resolving violin, veena, tabla, flute individually from the accompaniment stem) is a subsequent project stage and is not claimed or achieved by this fine-tuning run.

---

## 3. Base Model and Fine-Tuning Configuration

### 3.1 Base Architecture

The base model is HT-Demucs (Hybrid Transformer Demucs), from the `facebook/demucs` repository. The pretrained `htdemucs` checkpoint (4-stem: drums, bass, other, vocals) was loaded via the Demucs Python API and subsequently re-configured for 2-stem output.

### 3.2 2-Stem Initialization

A dedicated initialization script (`02_build_2stem_init.py`) was used to construct a 2-stem model from the 4-stem pretrained weights. The source ordering in the resulting model is:

```python
sources = ['vocals', 'accompaniment']
```

The accompaniment output head was initialized by averaging the pretrained weights of the drums, bass, and other heads from the 4-stem checkpoint. All other parameters (encoder, decoder, transformer, frequency embedding, channel up/downsampler) were copied exactly from the pretrained checkpoint.

The initialization checkpoint was verified as:

| Property | Value |
|---|---|
| Path | `D:\finetune_htdemucs_runs\init_2stem_model.pt` |
| File size | 168,131,208 bytes (~160 MB) |
| Sources | `['vocals', 'accompaniment']` |
| Trainable parameter entries | 356 |

### 3.3 Parameter Freezing

The initialization checkpoint records which parameters were designated as trainable (`trainable_param_names`). The training script respects this designation: only parameters in that set have `requires_grad = True`. All other parameters are frozen throughout fine-tuning.

---

## 4. Dataset

### 4.1 Source

The dataset is derived from the **Saraga corpus** of Carnatic and Hindustani music recordings. It was prepared into a structured directory layout under:

```
D:\dataset_prepared_saraga\
+-- train\
|   +-- <145 track directories>
+-- valid\
    +-- <15 track directories>
```

Each track directory contains three WAV files:

| File | Description |
|---|---|
| `mixture.wav` | Full mixture (vocals + accompaniment combined) |
| `vocals.wav` | Isolated vocal stem |
| `accompaniment.wav` | Isolated accompaniment stem |

### 4.2 Train/Validation Split

| Split | Tracks |
|---|---|
| Training | **145 tracks** |
| Validation | **15 tracks** |
| Total | 160 tracks |

The split was determined by the contents of the `train/` and `valid/` subdirectories. The dataset loader (`saraga_dataset.py`) uses the actual folder contents as ground truth, not a manifest file.

### 4.3 Duration-Weighted Crop Sampling

The dataset loader implements duration-weighted crop sampling, following the method used in the official Demucs `Wavset` class (`demucs/wav.py`). Each track contributes a number of crop-example slots proportional to its duration:

```
examples = ceil((duration - segment) / shift) + 1
```

With a 10-second segment and non-overlapping crops (shift = segment), this yields:

- **11,739 crop examples per training epoch** across 145 tracks
- **630 crop examples per validation epoch** across 15 tracks

Audio is read efficiently using `soundfile.SoundFile.seek()` and `read()`, avoiding loading full tracks into memory for a single short crop.

---

## 5. Dataset Compatibility and Audio Handling

### 5.1 Original Audio Configuration

All 160 tracks in the prepared Saraga dataset were confirmed to be **mono (1-channel)** audio at 44,100 Hz sample rate.

### 5.2 Mono/Stereo Dimensionality Issue

HT-Demucs expects stereo (2-channel) input tensors of shape `[batch, 2, samples]`. During the initial smoke test (Step 3.5), the first forward pass failed with a shape mismatch because the dataset returned tensors of shape `[1, 1, samples]` instead of the required `[1, 2, samples]`.

### 5.3 Dynamic Mono-to-Stereo Duplication

The dataset loader `saraga_dataset.py` was patched to perform **dynamic channel duplication** in `__getitem__`. Immediately after loading and padding each crop, the following conversion is applied when the loaded audio is mono:

```python
if mixture.shape[0] == 1:
    mixture = mixture.repeat(2, 1)
    vocals  = vocals.repeat(2, 1)
    accomp  = accomp.repeat(2, 1)
```

This produces stereo tensors by duplicating the mono channel, yielding a valid `[2, T]` mixture and `[2, 2, T]` target tensor for the model.

### 5.4 Source File Integrity

This conversion is applied entirely in RAM during data loading. **The original WAV files on disk were not rewritten, resampled, or modified in any way.**

---

## 6. Training Pipeline

### 6.1 Configuration

All values verified from `C:\iks_scripts\finetune_pipeline\04_train.py`.

| Parameter | Value |
|---|---|
| Segment length | 10.0 seconds |
| Sample rate | 44,100 Hz |
| Batch size | 1 |
| Gradient accumulation steps | 8 |
| Effective batch size | 8 |
| Optimizer | Adam |
| Learning rate | 1e-5 (fixed, no scheduler) |
| AMP precision | `torch.float16` |
| GradScaler | `torch.amp.GradScaler("cuda")` |
| Loss function | L1 loss (`torch.nn.functional.l1_loss`) |
| Maximum optimizer steps | 15,000 |
| Validation frequency | Every 500 optimizer steps |
| Checkpoint frequency | Every 500 optimizer steps |
| Early stopping patience | 15 validation checks |
| Early stopping min_delta | 1e-5 |
| DataLoader workers | 4 |
| Pin memory | True |

### 6.2 Optimizer Steps vs. Micro-Steps

Each optimizer step requires 8 micro-steps (individual forward/backward passes). The loss logged at each optimizer step is the L1 loss of the final micro-batch multiplied by `accum_steps`, restoring the approximate scale of the unaccumulated loss.

### 6.3 Approximate Epoch Equivalents

With 11,739 crop examples per epoch and effective batch size of 8:

```
Optimizer steps per epoch ~= 11,739 / 8 ~= 1,467
15,000 steps ~= 10.2 epochs  (approximate)
```

---

## 7. FP16 Mixed-Precision Training

### 7.1 Background: BF16 Incompatibility

The original training script was drafted with `torch.bfloat16` autocast. During memory probing, the forward pass failed with:

```
RuntimeError: cuFFT doesn't support tensor of type: BFloat16
```

HT-Demucs performs STFT operations internally, and the CUDA cuFFT library on the RTX 3050 Laptop GPU does not support BFloat16.

### 7.2 FP16 Transition

The autocast dtype was changed from `torch.bfloat16` to `torch.float16` in both the training loop and the validation function. A GradScaler was introduced to handle the reduced numerical range of FP16:

```python
scaler = torch.amp.GradScaler("cuda")

with torch.autocast(device_type="cuda", dtype=torch.float16):
    pred = model(mixture)
    loss = F.l1_loss(pred, target) / accum_steps
scaler.scale(loss).backward()

scaler.step(optimizer)
scaler.update()
```

No FP16 or GradScaler errors occurred across the entire 15,000-step run.

### 7.3 GradScaler State Persistence

The GradScaler's internal scale factor is preserved in every checkpoint (`"scaler_state": scaler.state_dict()`) and conditionally restored on resume, preventing scale reset across interruptions.

---

## 8. Validation and Early Stopping

### 8.1 Validation

Validation runs every 500 optimizer steps on all 15 held-out tracks. The validation metric is mean L1 loss computed under `torch.no_grad()` and `torch.float16` autocast, across all validation crop examples:

```
mean L1 loss = mean |predicted_stem - ground_truth_stem|
```

### 8.2 Early Stopping

| Parameter | Value |
|---|---|
| Patience | 15 validation checks |
| Min delta | 1e-5 |
| Check frequency | Every 500 optimizer steps |
| Max patience window | 7,500 optimizer steps (~5.1 epochs) |

**Early stopping did not trigger during the completed 15,000-step run.** The validation loss improved at every single one of the 30 validation checkpoints. The patience counter was 0 at training termination.

---

## 9. Checkpointing and Resume

### 9.1 Checkpoint Schema

```python
{
    "model_state":      model.state_dict(),
    "optimizer_state":  optimizer.state_dict(),
    "step":             <int>,
    "best_valid_loss":  <float>,
    "scaler_state":     scaler.state_dict(),
    "patience_counter": <int>,
}
```

### 9.2 Checkpoint Files

| File | Purpose |
|---|---|
| `latest.pt` | Most recently checkpointed state (every 500 steps and at termination) |
| `best.pt` | State corresponding to the lowest validation loss observed |

### 9.3 Actual Resume Event

The first segment of training was manually interrupted at approximately Step 9,000. The last successfully saved checkpoint was Step 8,500 (patience_counter = 0, best_valid_loss = 0.004613178414290323). Training was resumed from that checkpoint and continued correctly from Step 8,501 to Step 15,000 without resetting any state.

---

## 10. Training Progress and Results

### 10.1 Training Loss

| Milestone | Training L1 Loss |
|---|---|
| Step 1 (initial) | 0.01004 |
| Step 15,000 (final) | 0.00075 |

All 15,000 training-log entries were finite. No NaN or Inf values occurred.

### 10.2 Complete Validation Loss Progression

| Step | Validation L1 Loss |
|---|---|
| 500 | 0.00645 |
| 1,000 | 0.00584 |
| 1,500 | 0.00557 |
| 2,000 | 0.00538 |
| 2,500 | 0.00519 |
| 3,000 | 0.00506 |
| 3,500 | 0.00498 |
| 4,000 | 0.00491 |
| 4,500 | 0.00486 |
| 5,000 | 0.00481 |
| 5,500 | 0.00478 |
| 6,000 | 0.00474 |
| 6,500 | 0.00471 |
| 7,000 | 0.00468 |
| 7,500 | 0.00465 |
| 8,000 | 0.00463 |
| 8,500 | 0.00461 |
| 9,000 | 0.00459 |
| 9,500 | 0.00457 |
| 10,000 | 0.00455 |
| 10,500 | 0.00453 |
| 11,000 | 0.00451 |
| 11,500 | 0.00450 |
| 12,000 | 0.00449 |
| 12,500 | 0.00448 |
| 13,000 | 0.00447 |
| 13,500 | 0.00445 |
| 14,000 | 0.00444 |
| 14,500 | 0.00443 |
| **15,000** | **0.00442** |

**Total validation evaluations:** 30  
**Best validation L1 loss:** 0.00442 at Step 15,000  
**Percentage reduction (Step 500 to Step 15,000):** (0.00645 - 0.00442) / 0.00645 x 100 = **31.5%**

> **Important note on interpretation:** A decreasing validation loss indicates that model predictions are becoming closer to ground-truth stems on the held-out validation set. It does **not** constitute a formal source-separation evaluation. Objective metrics (SDR, SI-SDR, SIR, SAR) have not yet been calculated and are the subject of the next project stage.

### 10.3 Training Stability Summary

| Category | Status |
|---|---|
| NaN / Inf losses | None detected |
| CUDA Out-of-Memory | None |
| cuFFT errors | None (resolved by FP16 transition prior to run) |
| FP16 GradScaler errors | None |
| Dataset loading errors | None |
| Manual interruption | One (at ~Step 9,000); resumed cleanly from Step 8,500 |

---

## 11. Checkpoint Recovery After Training

### 11.1 Issue Detected

Upon completing the 15,000-step run, `best.pt` was found to be corrupted and could not be loaded. The corrupted file's size was approximately 845 MB, substantially larger than the expected ~459 MB. `latest.pt` was unaffected and loaded correctly. The exact low-level cause of the corruption was not conclusively established.

### 11.2 Recovery Procedure

Because Step 15,000 was simultaneously a validation improvement checkpoint and a periodic checkpoint interval, `latest.pt` contains the same model, optimizer, scaler, and metadata state as the intended `best.pt`. The recovery was performed as follows:

1. Read-only load of `latest.pt` with assertion of all six fields
2. Serialized to temporary file `best_recovered.tmp.pt` in the same directory
3. Independently loaded and verified the temporary file
4. Replaced corrupted `best.pt` with verified file via `os.replace()` (atomic on the same volume)
5. Temporary file removed automatically
6. Independently loaded and verified the recovered `best.pt`

### 11.3 Post-Recovery State

| Field | `best.pt` (recovered) | `latest.pt` |
|---|---|---|
| `step` | 15,000 | 15,000 |
| `best_valid_loss` | 0.004415826842771835 | 0.004415826842771835 |
| `patience_counter` | 0 | 0 |
| `model_state` | Present | Present |
| `optimizer_state` | Present | Present |
| `scaler_state` | Present | Present |
| File size | 481,261,667 bytes | 481,255,631 bytes |

`latest.pt` was not modified. No training was rerun. No log files were modified.

---

## 12. Final Fine-Tuned Model

### 12.1 Checkpoint Locations

| Checkpoint | Path |
|---|---|
| **Best model (recommended for evaluation)** | `D:\finetune_htdemucs_runs\run_002\best.pt` |
| Latest state | `D:\finetune_htdemucs_runs\run_002\latest.pt` |

Both checkpoints correspond to Step 15,000 and carry the same `best_valid_loss`. For the evaluation stage, **`best.pt` is the designated model artifact.**

### 12.2 Final Model Metadata

| Field | Value |
|---|---|
| Architecture | HT-Demucs (Hybrid Transformer Demucs) |
| Stem configuration | 2-stem: `['vocals', 'accompaniment']` |
| Base pretrained model | `htdemucs` (pretrained on MUSDB18) |
| Fine-tuning dataset | Saraga (145 train / 15 valid tracks) |
| Fine-tuning steps | 15,000 optimizer steps |
| Best validation L1 loss | **0.004415826842771835** |
| Best validation step | **15,000** |
| Early stopping triggered | No |
| Patience counter at end | 0 |
| File size (`best.pt`) | 481,261,667 bytes (~459 MB) |

### 12.3 Supporting Artifacts

| Artifact | Path |
|---|---|
| Initialization checkpoint | `D:\finetune_htdemucs_runs\init_2stem_model.pt` |
| Training script | `C:\iks_scripts\finetune_pipeline\04_train.py` |
| Dataset loader | `C:\iks_scripts\finetune_pipeline\saraga_dataset.py` |
| Training log | `D:\finetune_htdemucs_runs\run_002\train_log.txt` |
| Validation log | `D:\finetune_htdemucs_runs\run_002\valid_log.txt` |
| Smoke-test checkpoint (preserved) | `D:\finetune_htdemucs_runs\run_001\latest.pt` |

Exact command for the resumed final run:

```
C:\iks_scripts\venv\Scripts\python.exe 04_train.py ^
    --segment 10.0 ^
    --accum-steps 8 ^
    --max-steps 15000 ^
    --patience 15 ^
    --min-delta 1e-5
```

(Run from `C:\iks_scripts\finetune_pipeline\`, resumed from the Step 8,500 checkpoint in `run_002\latest.pt`.)

---

## 13. Limitations

1. **2-stem only.** This fine-tuning stage produces a model that separates audio into vocals and accompaniment. Individual-instrument isolation is a subsequent project stage.

2. **Validation loss is not SDR/SI-SDR/SIR/SAR.** The validation metric used during training is mean L1 loss. It is a useful training signal but does not constitute a formal source-separation quality assessment. Objective evaluation has not yet been conducted.

3. **Validation loss still decreasing at Step 15,000.** The validation loss was monotonically decreasing at training termination and early stopping did not trigger. Additional fine-tuning steps may produce further reduction in validation loss, though whether that would translate to perceptually meaningful or metrically significant improvement remains to be determined.

4. **Domain of evaluation.** The 15 validation tracks are drawn from the same Saraga corpus as the 145 training tracks. Generalization to Indian music recordings outside the Saraga collection has not been tested.

5. **Mono-to-stereo duplication.** Because the Saraga dataset is mono, the fine-tuned model was trained on artificially duplicated stereo input. The model has not been trained or validated on genuinely stereo Indian music recordings.

---

## 14. Fine-Tuning Completion Status

The HT-Demucs 2-stem fine-tuning stage of the IKS Music Source Separation and Instrument Isolation project is **COMPLETE**.

The resulting fine-tuned model checkpoint is:

```
D:\finetune_htdemucs_runs\run_002\best.pt
```

This model is ready to proceed to the next project stage: **objective source-separation evaluation** using a held-out evaluation set and standard metrics (SDR, SI-SDR, SIR, SAR), followed by qualitative listening inspection of separated stems on representative tracks.

---

## Appendix: Machine-Readable Summary

| Field | Value |
|---|---|
| `experiment_id` | `HTDemucs_2Stem_FineTuning` |
| `model` | `HT-Demucs (htdemucs, 2-stem fine-tuned)` |
| `dataset` | `Saraga (D:\dataset_prepared_saraga)` |
| `train_tracks` | `145` |
| `valid_tracks` | `15` |
| `segment_seconds` | `10.0` |
| `batch_size` | `1` |
| `accumulation_steps` | `8` |
| `effective_batch_size` | `8` |
| `learning_rate` | `1e-5` |
| `precision` | `float16` |
| `optimizer` | `Adam` |
| `max_steps` | `15000` |
| `best_validation_loss` | `0.004415826842771835` |
| `best_validation_step` | `15000` |
| `early_stopping_triggered` | `False` |
| `best_checkpoint_path` | `D:\finetune_htdemucs_runs\run_002\best.pt` |
| `latest_checkpoint_path` | `D:\finetune_htdemucs_runs\run_002\latest.pt` |
| `train_log` | `D:\finetune_htdemucs_runs\run_002\train_log.txt` |
| `valid_log` | `D:\finetune_htdemucs_runs\run_002\valid_log.txt` |
