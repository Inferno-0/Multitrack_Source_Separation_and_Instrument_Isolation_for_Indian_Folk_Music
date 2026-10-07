# FIGURE CAPTIONS

## Figure 1: run002_test_overall_sdr
**Caption:** Overall held-out TEST Source-to-Distortion Ratio (SDR) in decibels (dB), comparing the baseline model with the Run 002 fine-tuned model. Higher SDR indicates lower distortion. On the held-out TEST set, the fine-tuned model achieved higher mean positive SDR than the baseline.

## Figure 2: run002_test_per_instrument_sdr
**Caption:** Per-instrument mean positive SDR on the held-out TEST set for instruments with valid positive TEST representations. Fine-tuning substantially improved Flute SDR, while Tabla SDR remained approximately comparable to the baseline.

## Figure 3: run002_test_negative_rms
**Caption:** Mean negative-query RMS on the held-out TEST set, where lower values indicate lower output energy for queries corresponding to absent instruments. The dashed line denotes the $2\times$ safety threshold derived from the validation baseline and used during checkpoint selection; the TEST measurements shown here were obtained independently after model selection.

## Figure 4: run002_training_trajectory
**Caption:** Training trajectory of the Exponential Moving Average (EMA) of the L1SNR training objective across global optimizer steps during Run 002.

## Figure 5: run002_validation_trajectory
**Caption:** Validation trajectory of mean positive L1SNR across evaluation checkpoints during Run 002. Checkpoint selection was based on this validation objective subject to the predefined negative-query RMS safety condition.
