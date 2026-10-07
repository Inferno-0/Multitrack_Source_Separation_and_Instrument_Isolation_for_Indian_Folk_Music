# FIGURE GENERATION AUDIT

## A. Source Files Inspected
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\baseline_aggregate.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_aggregate.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\baseline_instruments.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_instruments.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\training_metrics.csv
- D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_metrics.csv

## B-H. Exact Source Fields and Data
### Figure: run002_test_overall_sdr
- **Metric:** Mean Positive SDR (dB)
- **Source:** baseline_aggregate.csv and run002_aggregate.csv
- **Values Plotted:** {"Baseline": 2.224826213504587, "Run 002": 4.222052335739136}
### Figure: run002_test_per_instrument_sdr
- **Metric:** Per-Instrument Positive SDR (dB)
- **Source:** baseline_instruments.csv and run002_instruments.csv
- **Values Plotted:** {"tabla (Base, Run002)": [0.909359896183014, 0.8574418306350708], "flute (Base, Run002)": [3.420704683796926, 7.280789158561013]}
### Figure: run002_test_negative_rms
- **Metric:** Mean Negative RMS
- **Source:** baseline_aggregate.csv and run002_aggregate.csv
- **Values Plotted:** {"Baseline": 0.0205222439687304, "Run 002": 0.0196397131665889}
### Figure: run002_training_trajectory
- **Metric:** EMA L1SNR Loss
- **Source:** training_metrics.csv
- **Values Plotted:** {"Start Step": 1401, "End Step": 2687, "Num Points": 1287}
### Figure: run002_validation_trajectory
- **Metric:** Mean Positive L1SNR (Validation)
- **Source:** validation_metrics.csv
- **Values Plotted:** {"Num Points": 6}

## I. SHA-256 Hashes of Generated Figures
- `run002_test_overall_sdr.png`: d09a4d0a02ccca89630cf3411ad2c5d57a85824e2c6dca09aaaa7c015ab2e48a
- `run002_test_overall_sdr.pdf`: 3b283aaa987ab67a33e2468e21a488e498ef173f37a4447c093d5988c2a0bf73
- `run002_test_overall_sdr.svg`: b12fc73469a0db3f6893c81dffc9e4eeda1b7dc9d754ea766c4be21eda82b1b7
- `run002_test_per_instrument_sdr.png`: d86c47ddd48cc1d79243f904447c5f390937bf62a8ebe30383e0a70e4be802d5
- `run002_test_per_instrument_sdr.pdf`: 97195ee3f1e490de11a5e0b10d9edeb1985d3476304019f5d8bfbed99aa4d0fd
- `run002_test_per_instrument_sdr.svg`: 94a354d2ed1213a72a8c391ac5fd6360b084d3ebed3d3c8173461e6df056b5e8
- `run002_test_negative_rms.png`: e6de325aaa9be7b6fd19f974ab123c3f17f7d9c4b2913c6717d9b0acf99bbb7e
- `run002_test_negative_rms.pdf`: 7b3ccac25af3122555e48af5b554a71cc36cb61d89a4417de084497a84c727f1
- `run002_test_negative_rms.svg`: 9c25ba6acfe2b9964c999b747f6f3e78b71e67019b6107ca55b64f6b2fa5904f
- `run002_training_trajectory.png`: cff5bb7d15aa426b2d6a732bebaabb7654209aca0382efb031f5339c8d2392fb
- `run002_training_trajectory.pdf`: bfc3104229c43972fed684a8fc7d4abc3ed95c53a97858733138f9f68b21f781
- `run002_training_trajectory.svg`: 6dcaa30afb0f8df6d4da4d3389d2a80491c52fd85f7a9150367f0b465b434ac0
- `run002_validation_trajectory.png`: 5f3e9939c4103864480f20e0d9bcde8dad4835a757e1465bde48067510d8a50d
- `run002_validation_trajectory.pdf`: b36f317503c3357f3444f64dde35df1a6bd143fbaa1c6541cc582ae36e0c43ee
- `run002_validation_trajectory.svg`: a91fcb3b3b676c9d4524d402e7c8dc00821baa1e5633e4645aa243faa5374d23

## J. Final Confirmation
NO locked research artifacts were modified.
All output matches the underlying verified data.

**FIGURE GENERATION STATUS: PASS**