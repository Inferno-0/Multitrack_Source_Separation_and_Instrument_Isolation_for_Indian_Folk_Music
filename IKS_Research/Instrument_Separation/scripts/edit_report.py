import sys
import re

def main():
    report_path = r"D:\IKS_Research\Instrument_Separation\reports\IKS_Internship_Complete_Project_Report.md"
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Rule 3 & 6: Cascade vs Instrument Isolation & Architecture Concept
    old_cascade = """### 11.1 Architecture concept
The project utilized Banquet, an architecture that injects a conditioning "query" into the HT-Demucs backbone. The conceptual research cascade was formulated as:
**Indian folk recording → Fine-tuned HT-Demucs → Accompaniment → Banquet + instrument query → Target instrument**

However, the final quantitative evaluation (Run 002) specifically evaluated the controlled mixture stage independent of the cascade:
**Controlled instrument mixture + instrument query → Banquet → target instrument**"""
    
    new_cascade = """### 11.1 Architecture concept
The project subsequently extended the investigation from two-stem vocal/accompaniment separation to query-conditioned instrument isolation using the Banquet architecture. The conceptual research pipeline was formulated as a cascade in which Indian folk recordings could first undergo vocal/accompaniment separation using the fine-tuned HT-Demucs model, after which a query-conditioned Banquet model could be used to target an individual instrument. However, the final quantitative Run 002 evaluation was conducted on controlled synthetic instrument mixtures with isolated ground-truth sources and was therefore an evaluation of the query-conditioned instrument-separation stage rather than a quantitative end-to-end evaluation of the complete HT-Demucs → Banquet cascade on naturally recorded folk mixtures."""
    if old_cascade in content:
        content = content.replace(old_cascade, new_cascade)
    else:
        print("Failed to replace old_cascade")

    # Rule 7: Controlled Mixture Wording
    old_controlled = "By generating synthetic mixtures from this library, the project created controlled mixtures with exact source targets for query-conditioned training."
    new_controlled = "For the instrument-isolation experiments, curated isolated recordings were used to construct controlled mixtures for evaluating query-conditioned source extraction."
    if old_controlled in content:
        content = content.replace(old_controlled, new_controlled)

    # Rule 8: Harmonium, Dholak and Dhul TEST-set limitation
    old_test_limit = "Positive TEST SDR was unavailable for Harmonium, Dholak, and Dhul because the available source inventory did not provide sufficient eligible recordings satisfying the source-level partitioning and temporal non-overlap requirements. These classes were therefore not assigned zero performance values; their positive TEST performance remains unmeasured."
    new_test_limit = "Positive TEST-set SDR results were not available for Harmonium, Dholak, and Dhul because the final TEST inventory did not contain sufficient positive query cases for these instruments. Consequently, no positive-separation performance claim is made for these instruments."
    if old_test_limit in content:
        content = content.replace(old_test_limit, new_test_limit)

    # Rule 10: Do not overclaim feasibility
    old_feasibility = "These findings indicate measurable improvement for the evaluated instrument classes, but they do not establish uniform performance across all target instruments or equivalent performance on naturally occurring folk recordings."
    new_feasibility = "The experiments provide evidence that query-conditioned instrument separation can be applied to selected Indian folk-music instrument recordings and can produce measurable improvements on unseen test mixtures for the instrument cases represented in the final TEST inventory."
    if old_feasibility in content:
        content = content.replace(old_feasibility, new_feasibility)

    # Rule 11: Remove unsupported internal-representation claims
    old_internal = "Across different folk traditions, the pretrained model's predefined source categories did not consistently correspond to the instrumentation present in the evaluated Indian folk recordings. In several evaluated recordings, substantial tabla/dholak energy was observed in the estimated vocal output. This may be related to acoustic overlap between these instruments and the source categories represented during pretraining."
    new_internal = "The baseline evaluation indicated a mismatch between the source categories represented by the pretrained separation model and the instrumentation encountered in the evaluated Indian folk-music recordings. This mismatch was reflected in inconsistent allocation of instrumental content between the vocal and accompaniment stems and recurring interference from non-vocal sources. The subsequent fine-tuning experiments were therefore designed to examine whether adaptation to culturally relevant musical material could improve separation behaviour."
    if old_internal in content:
        content = content.replace(old_internal, new_internal)

    # Rule 17: EXACT LOCKED RUN 002 RESULTS
    old_results = """- **Mean positive-query SDR:** Mean positive-query SDR across the available positive TEST cases increased from 2.225 dB (Baseline) to 4.222 dB.
- **Flute SDR:** Improved from 3.421 dB to 7.281 dB.
- **Tabla SDR:** Remained approximately stable (0.909 dB to 0.857 dB).
- **Mean Negative RMS:** Decreased from 0.0205 to 0.0195, reflecting an observed improvement in negative-query suppression behavior and slightly lower output energy for absent-target queries."""

    new_results = """TEST SET

Global Positive SDR:
Baseline = 2.225 dB
Run 002 = 4.222 dB
Absolute change = +1.997 dB

Global Positive L1SNR:
Baseline = -3.023
Run 002 = -4.285
Absolute change = -1.262

Global Mean Negative RMS:
Baseline = 0.0205
Run 002 = 0.0195

Per-instrument Positive SDR:

Tabla:
Baseline = 0.909 dB
Run 002 = 0.857 dB
Change = -0.052 dB

Flute:
Baseline = 3.421 dB
Run 002 = 7.281 dB
Change = +3.860 dB

Negative RMS:

Tabla:
Baseline = 0.0344
Run 002 = 0.0380

Flute:
Baseline = 0.0016
Run 002 = 0.0015

Dholak:
Baseline = 0.0293
Run 002 = 0.0292

Dhul:
Baseline = 0.0166
Run 002 = 0.0097"""
    if old_results in content:
        content = content.replace(old_results, new_results)

    # Rule 18: VALIDATION VS TEST MUST BE CLEARLY DISTINGUISHED
    old_validation = "The Run 002 checkpoint at global step 2600 was selected using the predefined fixed validation procedure, based on improvement in the primary validation L1SNR objective while satisfying the negative-query RMS safety constraint."
    new_validation = """The Run 002 checkpoint at global step 2600 was selected using the predefined fixed validation procedure, based on improvement in the primary validation L1SNR objective while satisfying the negative-query RMS safety constraint.

VALIDATION was used for checkpoint selection.
TEST was independently held out and used only for final evaluation.

Validation:
Baseline L1SNR = -2.219
Run 002 best L1SNR = -2.609

Validation:
Baseline SDR = -1.564 dB
Run 002 best SDR = -1.674 dB

TEST:
Baseline SDR = 2.225 dB
Run 002 SDR = 4.222 dB"""
    if old_validation in content:
        content = content.replace(old_validation, new_validation)

    # Fix the \f bug in the checkpoint path at the end of the file
    if r"D:\IKS_Research\Instrument_Separationinetune_banquet_runsun_002 est.ckpt" in content:
        content = content.replace(r"D:\IKS_Research\Instrument_Separationinetune_banquet_runsun_002 est.ckpt", 
                                  r"D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\best.ckpt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Edits applied to the report.")

if __name__ == "__main__":
    main()
