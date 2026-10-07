# Pilot Mixture Generation Report (1-Example Test)

**Date:** 2026-08-26

## 1. Single-Example Design
A single synthetic pilot mixture (`pilot_example_0`) was successfully generated to test the pipeline before scaling up.

### Mixture Composition:
- **Vocals:** Yes
- **Instruments:** Tabla, Flute
- **Target Instrument:** Flute

### Alignment and Duration:
- The mixture and active stems were extracted as precisely aligned **6.0-second** chunks.
- Sample rate: 44,100 Hz.
- The target stem (`target.wav`) corresponds exactly to the clean `flute.wav` mixed into the track.

### Mixing and Normalization:
- Instruments were mixed using standard linear addition with a 0.5 gain reduction.
- Peak normalization was applied safely to cap the mix at 0.9 amplitude (anti-clipping measure).
- All source components (vocals, tabla, flute) were saved separately alongside `mixture_clean.wav` to guarantee ground-truth recoverability.

## 2. Query Handling
- A completely independent flute recording (different `original_filename` than the flute in the mixture) was selected as the `query_source` by pulling from the `TRAIN` split's query-eligible pool.
- The query chunk was extracted precisely at **10.0 seconds**, fulfilling Banquet's strict query constraints.

### Artifacts Location:
`D:\IKS_Research\Instrument_Separation\mixtures\pilot_example_0\`
