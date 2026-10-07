# EXP002 Conclusions

## Hypothesis Evaluation
The qualitative observations generally support the hypothesis. HTDemucs successfully separated vocals and accompaniment while exhibiting recurring leakage in certain cases.

## Principal Findings
1. HTDemucs consistently isolated the lead vocalist while maintaining intelligibility.
2. The accompaniment generally remained complete and musically coherent.
3. Flute leakage into the vocal stem was the most consistent qualitative limitation.
4. Secondary vocal components such as background singing, whistles and vocal calls were more difficult to suppress completely.
5. The experiment establishes a qualitative baseline for future work on Indian folk music source separation.

## Strengths
- Vocal separation
- Vocal naturalness
- Accompaniment preservation
- Consistency
- Low artifacts

## Limitations
- Flute leakage
- Secondary vocal leakage
- Occasional percussion leakage
- One outlier recording

## Research Implications
The experiment demonstrates that HTDemucs is suitable as a baseline model for Indian folk music source separation. The findings identify clear directions for improving the model through fine-tuning and expanded source separation.

## Future Work
- Fine-tune HTDemucs using Indian folk music.
- Reduce flute leakage.
- Improve suppression of secondary vocal components.
- Extend source separation toward a limited number of primary folk instruments (rather than attempting complete instrument isolation).
- Compare future fine-tuned models against this qualitative baseline.

## Final Conclusion
The evaluation confirms that pretrained HTDemucs provides a robust starting point for separating vocals and accompaniment in Indian folk music. Establishing this baseline clarifies the model's inherent limitations with traditional instruments and provides a clear framework for targeted fine-tuning in subsequent experimental phases.
