# EXP004 Conclusions

## Overall Finding
Within the five-recording qualitative sample evaluated, baseline HT-Demucs produced consistent and usable two-stem separation for Pandavani recordings.

## Vocal Separation
Vocal outputs were generally clean and natural with only minor residual non-vocal material.

## Accompaniment Preservation
The No-Vocals outputs retained the accompaniment effectively without noticeable vocal leakage.

## Leakage and Failure Case
The principal observed limitation was the presence of minor residual non-vocal material in the Vocals outputs. However, no noticeable vocal leakage was identified in the No-Vocals outputs, and no major instrument-specific failure case was identified in this sample.

## Artifacts and Naturalness
No major audible artifacts, such as metallic sounds, warbling, or robotic vocal textures, were identified.

## Reconstruction and Processing Robustness
The physical chunking, overlap, HT-Demucs inference, and reconstruction pipeline successfully preserved full recording duration and did not produce audible boundary problems or artifacts during manual listening. This successful use of the established processing architecture demonstrates that the established processing architecture successfully handled the tested recordings across substantially different durations while preserving the original recording length.

## Research Implication
This baseline experiment serves as evidence for the next stages of the research. It demonstrates the robustness of the physical chunking production pipeline and indicates that baseline HT-Demucs produced good qualitative separation on this specific dataset sample for two-stem separation. However, this result does not establish quantitative separation performance, nor does it guarantee generalization to all Pandavani recordings or other Indian folk traditions. Furthermore, it does not claim to solve individual instrument isolation.

## Limitations
- The qualitative evaluation covers five Pandavani recordings only.
- The evaluation is entirely manual and subjective.
- No ground-truth isolated stems were available for these real-world recordings.
- The findings describe the qualitative behavior of HT-Demucs on these tested recordings and should not be interpreted as a quantitative benchmark of general model performance.
- The absence of noticeable artifacts during listening does not prove perfect source separation.
- Minor residual non-vocal components were perceptible in the Vocals outputs.

## Objective Evaluation Status
Objective evaluation using SDR, SI-SDR, SIR, SAR, or related quantitative metrics has not been calculated for EXP004. Objective evaluation remains pending.
