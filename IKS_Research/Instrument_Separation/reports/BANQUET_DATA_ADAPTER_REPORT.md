# Banquet Data Adapter Implementation Report

**Date:** 2026-08-26

## 1. MoisesDB Decoupling Strategy
The original Banquet repository's dataset (`MoisesDBBaseDataset`) requires a highly specialized directory hierarchy populated with `stem.query.npy` and `stem.npy` files. Attempting to spoof this structure with our dataset would require a massive and redundant data duplication effort.

**Decision:** We will create a custom PyTorch dataset module (`IKSSourceSeparationDataset`). It directly consumes the CSV metadata we generated in the splitting phase, locates the pre-mixed WAV files in our `mixtures` folder (or mixes them dynamically in memory), and generates the exact tensor dictionaries expected by Banquet. 

## 2. Interface Alignment
Based on the repository code (`train.py` and `bandit.py`), Banquet's data ingest requires specific tensor dimensionalities and key names. The custom adapter is designed to strictly output:
```python
{
    "mixture": {"audio": torch.Tensor}, # Shape: [2, 264600]
    "query": {"audio": torch.Tensor},   # Shape: [2, 441000]
    "sources": {"target": torch.Tensor},# Shape: [2, 264600]
    "metadata": {"stem": str}           # e.g., "flute"
}
```

## 3. Real-Time Conversion & Safety
1. **Mono to Stereo:** Since our WAV sources and the `demucs_accompaniment.wav` are mono, the adapter applies `.unsqueeze(0).repeat(2, 1)` to correctly broadcast `[1, N]` to `[2, N]`.
2. **Negative Handling:** If the target instrument is NOT present in the mixture (negative example), the adapter will yield `torch.zeros((2, 264600))` for the `sources["target"]`.
3. **Hardware & Type Casting:** Tensors will strictly be cast to `torch.float32`.

**STATUS:** **READY.** The data adapter logic conforms natively to the Banquet Lightning module constraints and is safe for implementation.
