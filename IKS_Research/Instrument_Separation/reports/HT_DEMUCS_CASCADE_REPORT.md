# HT-Demucs Cascade Report (1-Example Test)

**Date:** 2026-08-26

## 1. Checkpoint Loading
The fine-tuned cascade checkpoint was explicitly evaluated:
- **Target:** `D:\finetune_htdemucs_runs\run_002\best.pt`
- **Result:** Loaded successfully using PyTorch Lightning `state_dict` unpacking into a manually instantiated `HTDemucs` instance.

## 2. Input/Output Parameters
- **Input Mixture:** `pilot_example_0\mixture_clean.wav` (Mono duplicated to Stereo).
- **Sample Rate:** 44,100 Hz strictly maintained.
- **Input Tensor Shape:** `[1, 2, 264600]` (1 Batch, Stereo, 6.0 Seconds).

## 3. Forward Pass & Outputs
The `demucs.apply.apply_model` function executed cleanly without out-of-memory or shape-mismatch errors. 
- **Output Tensor Shape:** `[2, 2, 264600]` (2 Sources, Stereo, 6.0 Seconds).
- The output was correctly unpacked and averaged to mono for storage efficiency (as Banquet will dynamically handle mono->stereo conversion later if desired, or we can feed the stereo file directly).

### Artifacts Written:
- `D:\IKS_Research\Instrument_Separation\demucs_outputs\pilot\pilot_example_0\demucs_vocals.wav`
- `D:\IKS_Research\Instrument_Separation\demucs_outputs\pilot\pilot_example_0\demucs_accompaniment.wav`

**CONCLUSION:** **PASS.** The generated `demucs_accompaniment.wav` is non-empty, precisely aligned to the original 6.0s duration, and is fully ready to be ingested by the Banquet query-conditioner as the realistic input mixture containing authentic HT-Demucs degradation artifacts.
