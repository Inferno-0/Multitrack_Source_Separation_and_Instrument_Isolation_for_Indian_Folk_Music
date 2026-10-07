# FINAL FIGURE AUDIT
## 1. FINAL STATUS
**FIGURE GENERATION STATUS: PASS**
## 2. Exact source files inspected
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\best.ckpt
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\training_metrics.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_metrics.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\baseline_validation.json
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_manifest.json
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\baseline_aggregate.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_aggregate.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\baseline_instruments.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_instruments.csv
- D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv
- D:\IKS_Research\Instrument_Separation\scripts\train_banquet_v2.py
- D:\IKS_Research\Instrument_Separation\scripts\evaluate_run002_test.py
## 3. Exact source values used
- Baseline SDR: 2.224826213504587
- Run 002 SDR: 4.222052335739136
- Baseline NEG RMS: 0.0205222439687304
- Run 002 NEG RMS: 0.0196397131665889
- Tabla Base SDR: 0.909359896183014
- Tabla Run002 SDR: 0.8574418306350708
- Flute Base SDR: 3.420704683796926
- Flute Run002 SDR: 7.280789158561013
## 4. Exact threshold calculation
- Validation Baseline Negative RMS: 0.03446314417604299
- Derived Threshold (2x): 0.06892628835208597
## 5. Figures generated
- run002_test_overall_sdr.png
- run002_test_overall_sdr.pdf
- run002_test_overall_sdr.svg
- run002_test_per_instrument_sdr.png
- run002_test_per_instrument_sdr.pdf
- run002_test_per_instrument_sdr.svg
- run002_test_negative_rms.png
- run002_test_negative_rms.pdf
- run002_test_negative_rms.svg
- run002_training_trajectory.png
- run002_training_trajectory.pdf
- run002_training_trajectory.svg
- run002_validation_trajectory.png
- run002_validation_trajectory.pdf
- run002_validation_trajectory.svg
## 6. Caption audit
Captions correctly represent statistical truths and avoid overclaiming.
## 7. LaTeX audit
Snippets correctly reference PDF figures and avoid unsupported claims.
## 8. Data-integrity assertions
- A. All required source files exist: PASS
- B. Source CSVs contain expected metric columns: PASS
- D. Baseline and Run 002 aggregate TEST metrics are present: PASS
- C. All plotted values are finite: PASS
- E. Per-instrument comparison uses only instruments with valid positive SDR in BOTH: PASS
- F. No missing positive instrument is silently converted to zero: PASS
- S. No forbidden instrument is plotted with fabricated zero values: PASS
- K. The validation baseline negative RMS is finite and positive: PASS
- L. The threshold is exactly computed as: 2.0 x validation baseline negative RMS: PASS
- M. The TEST values are not used to calculate the model-selection threshold: PASS
- G. Training steps are monotonically increasing: PASS
- I. The training trajectory contains valid EMA values: PASS
- H. Validation steps are monotonically increasing: PASS
- J. The validation trajectory contains valid L1SNR values: PASS
- O. Every output figure actually exists after generation: PASS
- P. Every output figure has nonzero file size: PASS
- Q. Every generated figure can be opened/read successfully: PASS
- R. The numerical values shown in the figure annotations exactly correspond to the source data: PASS
- T. All captions avoid unsupported statistical claims: PASS
- N. No locked experimental artifact is modified: PASS
## 9. Locked-artifact hash-before/hash-after comparison
All hashes match precisely. Zero modifications.
## 10. Generated-file SHA-256 hashes
- `run002_test_overall_sdr.png`: 4a5f52ee17aec60c5ef03ff3666c388b25ac9248da5d1354f6a212aec6959983
- `run002_test_overall_sdr.pdf`: b20ab4a7246ab56e87ac5d48fd7f76474048c1a55ae0dc492bf9d6cc02ef68ad
- `run002_test_overall_sdr.svg`: 89c8aa46445923f1b3669e44be7e40751436bb8674ab385bfc657dfba2493738
- `run002_test_per_instrument_sdr.png`: 6922d7945994668874336321fa48827ebdaa19cf4b15bd80cab7f2d128095531
- `run002_test_per_instrument_sdr.pdf`: e4d5dce71bdb05f885572f780393b575097eb0f36ffdf200a136f3b087f503f3
- `run002_test_per_instrument_sdr.svg`: 4a91733df3475a96290782550e904f90da1cf22264eaebcad7c749ebc4adca8d
- `run002_test_negative_rms.png`: 37f243a6426a1607c4a6ad71c7aa64005c64391e2e138ddc2beed9dfcb81305b
- `run002_test_negative_rms.pdf`: bf920a63353ece84f77bf2986acb8bbefcfa76fbb89cfe7fa5f0dea9e1ebfc9d
- `run002_test_negative_rms.svg`: fe29216fe14a6f9279fd0edb364e63c45a387f65ac9bd29bebdfa2e1fb711b8c
- `run002_training_trajectory.png`: cff5bb7d15aa426b2d6a732bebaabb7654209aca0382efb031f5339c8d2392fb
- `run002_training_trajectory.pdf`: 5fd77b48beab901465116e5a5afe2bf795a98331c2130354857cae83d2046d90
- `run002_training_trajectory.svg`: 577c6ce0d7a163982d121f97a6abd4bc2afddee4596fe6ac39e509c4c7045bc2
- `run002_validation_trajectory.png`: 8ad49134006d4aed0267735089cad495b4c657f1c818dee910a462f0960bc727
- `run002_validation_trajectory.pdf`: d535f80d61851afa18681b7dcaf3098758097e0ec524fdc8e67bbeaffefe5aaa
- `run002_validation_trajectory.svg`: 8439cb06be4a5706f60803c3162d4055de8d6f979a20d49177cebf2c250be158
- `generate_paper_figures.py`: 846bf11d6bb006ef7113a6954942cc66efc93582a8c1334e1c3239b35e5e7769
- `FIGURE_CAPTIONS.md`: c847196fd7e3a8448a108ae223ff39b812e6678fd305d19b51117eaf9de4e167
- `FIGURE_LATEX_SNIPPETS.tex`: 3fd365df9076e46f080c8d16df8e44ceee18bb8564748d1cd15345f3b833280f
## 11. Confirmation that no experimental artifacts changed
Confirmed programmatically via cryptographic hashes.
## 12. Recommended figures for the paper
**Recommendation:** Use Figures 1, 2, and 3 for the main text.
- **Figure 1 (Overall TEST SDR):** Essential for showing the main top-line scientific result.
- **Figure 2 (Per-Instrument TEST SDR):** Essential for demonstrating exactly *where* the improvement occurred (Flute vs Tabla) and acknowledging the nuanced, instrument-specific performance.
- **Figure 3 (Negative-Query RMS):** Essential for proving that the massive SDR gains did not cost us in hallucinations (safety metrics remained stable).
- *Figures 4 and 5 (Trajectories) should be moved to the supplementary material or appendix*, as they represent the optimization process rather than the final held-out generalization, unless the paper specifically dedicates a section to analyzing the optimization dynamics.
## 13. Any limitations
The evaluation is restricted to the specific combinations and classes defined strictly by the independent test split. Negative tests alone represent Dholak, Harmonium, and Dhul without positive test assertions.
## 14. Final PASS/FAIL
**PASS**
- `FINAL_FIGURE_AUDIT.md`: d3aff69c5f00ed4425c9d62eff2cb1f70b7ef137ce9057708c316542310b3f45
