# Banquet Repository Audit Report

**Date:** 2026-08-26
**Repository:** `kwatcharasupat/query-bandit`
**Target Pipeline:** Stage 5 - Instrument Separation

---

## 1. Environment & Setup

- **Python Version:** 3.14.6
- **PyTorch Configuration:** `2.13.0+cpu`. Note: A dedicated virtual environment (`C:\iks_scripts\banquet_venv`) was successfully created and populated. However, standard precompiled PyTorch CUDA wheels (cu118/cu121/cu124) do not currently support Python 3.14. Therefore, the pip installation falls back to a CPU-only build.
- **Hardware Profile:** NVIDIA GeForce RTX 3050 (4 GB VRAM).
- **CUDA Availability:** `False` (due to Python 3.14 wheel constraints).
- **Memory Considerations:** Banquet usually trains with a batch size of 12 on a 24 GB RTX 4090. Given the 4 GB VRAM limitation of the RTX 3050, fine-tuning will require a severely restricted batch size (e.g., 1 or 2) combined with gradient accumulation.

## 2. Dataset Interface Requirements

The Banquet dataset classes (`core/data/moisesdb/dataset.py`) are strictly coupled to the MoisesDB `.npy` folder structure. The exact data requirements are:

- **A. Target Stems:** Supports 45 fine-level stems including `drums`, `bass_guitar`, `clean_electric_guitar`, `flutes`, etc.
- **B. Target Segment Length:** Default training chunk size is **6.0 seconds**.
- **C. Target Representation:** Raw audio array of shape `(channels, samples)`.
- **D. Mixture Sample Rate:** Must be exactly **44,100 Hz** (`model_fs: 44100`). The inference code resamples automatically if there's a mismatch, but native 44.1kHz is preferred for training.
- **E. Mixture Channels:** **2 Channels (Stereo)** (`in_channel: 2`). *Important Note:* The IKS prepared dataset is currently Mono. Banquet strictly expects a stereo input matrix.
- **F. Query Representation:** Audio array of shape `(channels, samples)`.
- **G. Target-Query Pairing Generation:** The dataset internally handles query selection. By default (`use_own_query: False`), it selects a random song containing the requested target stem and extracts its query to prevent source-level leakage.
- **H. Query Shape/Format:** Raw stereo audio array.
- **I. Expected Query Duration:** Strictly **10.0 seconds**. (`assert query_length_seconds == 10.0, "Only 10s queries are supported"`)
- **J. Query Duration Mismatch Handling:** If a query is provided at a different duration during inference, Banquet forcefully pads (by tiling/looping) or truncates the query array to exactly 10.0s *before* passing it to the network.
- **K. Mixture Loading:** `MoisesDataModule` natively handles mixture/stem loading using memmaped `.npy` chunks rather than `.wav` files directly.
- **L. Pre-mixing Scaling:** Training applies dynamic data augmentation via `SmartGain` (range -6 dB to 6 dB based on signal energy).

## 3. Pre-trained Model Assessment

- **M. Model Architecture & Parameters:** `PasstFiLMConditionedBandit`. As stated in the original literature, the trainable parameter count is **24.9 Million**.
- **N. Checkpoint Availability:** The `ev-pre-aug.ckpt` weights were successfully downloaded from Zenodo (`13694558`). The final file size is ~645 MB, encompassing the model state dictionary, optimizer state, and PyTorch Lightning trainer metadata.
- **O. Fine-Tuning/Inference API:** Banquet uses PyTorch Lightning's `EndToEndLightningSystem.load_from_checkpoint` which seamlessly integrates with standard PyTorch dataloaders. Inference is exposed via `inference_byoq()` in `train.py`.

## 4. Key Takeaways for Synthetic Mixture Design

To construct the leakage-safe synthetic training set for Banquet, the following parameters are now strictly defined:

1. **Audio Format:** The 44.1kHz mono files from `D:\ISOLATED_INSTRUMENTS_PREPARED` must be duplicated to stereo arrays during the mixture generation phase.
2. **Chunk Size:** Training mix durations should be designed around **6.0 seconds**.
3. **Query Length:** Queries must be exactly **10.0 seconds** (or tileable to 10 seconds).
4. **Data Format:** To utilize the existing `MoisesDataModule` natively without heavy modification, we must serialize the generated mixtures and queries into memory-mapped `.npy` files instead of standard `.wav` files.
