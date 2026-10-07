# Objective Evaluation: EXP004

## Purpose
The purpose of this objective evaluation is to computationally assess the separation quality of the HT-Demucs model on the target folk music recordings using standardized source separation metrics.

## Evaluation Metrics Used
The evaluation leverages the following standard objective metrics:
- **SDR (Source to Distortion Ratio):** Measures overall separation quality.
- **SI-SDR (Scale-Invariant SDR):** Provides a robust measure of separation performance independent of signal scaling.
- **SIR (Source to Interference Ratio):** Measures the degree of leakage or interference from other sources.
- **SAR (Source to Artifacts Ratio):** Quantifies the absence of algorithmic artifacts introduced during separation.

## Expected Outputs
The evaluation pipeline is expected to produce:
- **metrics/**: Data files (CSV/JSON) containing the computed SDR, SI-SDR, SIR, and SAR values.
- **plots/**: Visualizations such as metric distributions and comparison charts.
- **reports/**: Summarized markdown or PDF reports of the objective findings.
- **logs/**: Execution logs generated during the evaluation process.
- **notebook/**: Any exploratory notebooks used during the analysis phase.

## Relationship with the Baseline Experiment
This objective evaluation corresponds directly to the source separation outputs generated in EXP004. It follows the standardized quantitative evaluation framework established in EXP002 to assess the model's performance on a distinct subset of recordings.
