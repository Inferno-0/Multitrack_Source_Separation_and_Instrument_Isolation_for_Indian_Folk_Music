# Banquet Implementation Inspection Report

**Date:** 2026-08-26
**Target Pipeline:** Stage 5 - Instrument Separation

## 1. Repository Structure & Model
- **Repository Structure:** Based on PyTorch Lightning. Contains config YAMLs via Hydra/OmegaConf. The main entry point is `train.py`.
- **Model Construction:** `PasstFiLMConditionedBandit`. Combines a query encoder (PaSST) with a separator (Bandit bandsplit module) using FiLM conditioning.
- **Checkpoint Format:** Standard PyTorch Lightning `.ckpt` archive (ZIP), size ~645 MB, containing optimizer states, state_dict, and hyperparameters. Parameters: **24.9M**.

## 2. Interface Requirements
- **Input Tensor Shapes:** Mixture input `(B, 2, Samples)`. Expected sample rate: 44,100 Hz.
- **Query Tensor Shapes:** Query input `(B, 2, Samples)`. 
- **Training Segment Requirements:** Default `chunk_size_seconds` is **6.0s**. 
- **Query-Duration Requirements:** Strictly **10.0s**. Inference forcefully pads/truncates.
- **Channel Handling:** Expected **Stereo (2 channels)**. IKS Prepared dataset is Mono, thus requires on-the-fly duplication or pre-duplication to stereo.
- **Dataset Assumptions:** Strongly tied to MoisesDB folder structure, requiring pre-extracted `.npy` arrays for mixture and queries.

## 3. Training Internals
- **Target Stem Selection:** Random chunk extraction, random query from the same class. 
- **Loss Function:** `L1SNRLoss` or `L1SNRDecibelMatchLoss` (L1 distance in time domain + SNR).
- **Optimizer / Scheduler:** Adam optimizer with `ReduceLROnPlateau` or `CosineAnnealingLR`.
- **Memory Requirements:** 24.9M parameter model requires heavy activations for a 6s stereo chunk at 44.1kHz. A 4GB RTX 3050 will strictly require batch size = 1 or 2 with gradient accumulation.
- **Inference API:** `system.chunked_inference(batch)` runs the model over overlapping chunks of long audio.

## 4. Required Changes for Our Synthetic Dataset
The existing `MoisesDataModule` and `MoisesDBBaseDataset` cannot be cleanly used without faking an extensive folder structure and converting all files to `.npy`. 
**Decision:** We will write a custom `LightningDataModule` (`IKSSourceSeparationDataModule`) and PyTorch `Dataset` that reads our specific metadata files, randomly mixes the chosen 6s stems on the fly (or reads from a pre-mixed Pilot WAV folder), and serves them in the expected tensor dictionary format:
```python
batch = {
    "mixture": {"audio": mix_tensor},
    "query": {"audio": query_tensor},
    "sources": {"target": target_tensor},
    "metadata": {"stem": [target_class]}
}
```
This is drastically safer and cleaner than reverse-engineering the MoisesDB memmap layout.
