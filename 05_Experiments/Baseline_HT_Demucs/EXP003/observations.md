# EXP003 Observations

## Experiment Information
- **Experiment ID:** EXP003
- **Dataset:** BAUL_GEET (Baul Geet)
- **Model:** HT-Demucs (htdemucs)
- **Separation type:** Two-stem music source separation (Vocals and No-Vocals)
- **Number of recordings:** 3
- **Evaluation method:** Manual qualitative listening evaluation

## BAUL_002

1. **Vocal Separation Quality:** The model has well isolated the singer's voice from the original recording. The voice is clear, lyrics are understandable, and no background music remains. The vocal sounds complete with no noticeable instruments mixed into the vocals.
2. **Vocal Leakage:** Nothing that belongs to the accompaniment can be heard in the Vocals output, and nothing that belongs to the vocals can be heard in the No-Vocals output. No noticeable leakage was detected in either direction.
3. **Instrument Leakage:** No instruments have leaked into the Vocals output.
4. **Accompaniment Quality:** The No-Vocals output sounds like real music. No important instruments are missing, and it does not sound hollow or empty. It sounds natural without weakened instruments or sudden changes in volume or sound.
5. **Audio Artifacts:** No unnatural sounds have been introduced by the separation process.
6. **Vocal Naturalness:** The separated vocal sounds like a natural human performance.
7. **Instrument Preservation:** The original instruments have been properly preserved in the No-Vocals output.
8. **Balance Between Vocals and Accompaniment:** The separation feels balanced between the two outputs.
9. **Overall Separation Quality:** Vocals and accompaniment are clear with no vocal or instrument leakage and no major artifacts. Vocals are natural and instruments are preserved. Overall, the outputs are usable.
10. **Additional Observations:** The distinctive observation for this recording is the absence of noticeable vocal and instrument leakage, which is a positive result.

## BAUL_016

1. **Vocal Separation Quality:** The model has well isolated the singer's voice from the original recording.
2. **Vocal Leakage:** No vocal leakage was heard in the No-Vocals output.
3. **Instrument Leakage:** Ektara has leaked completely into the Vocals output. This is the principal problem observed in BAUL_016.
4. **Accompaniment Quality:** The No-Vocals output sounds complete and natural.
5. **Audio Artifacts:** No unnatural or distorted sounds have been introduced by the separation process.
6. **Vocal Naturalness:** The separated vocals sound like a natural human performance.
7. **Instrument Preservation:** All the original instruments have been preserved well in the No-Vocals output.
8. **Balance Between Vocals and Accompaniment:** The separation is balanced between the two outputs.
9. **Overall Separation Quality:** Vocals and accompaniment are clear with no vocal leakage and no major artifacts. Vocals are natural and instruments are preserved. Ektara leakage is prominently present in the Vocals output. The outputs are usable if the Ektara leakage is removed.
10. **Additional Observations:** No additional observations.

## BAUL_024

1. **Vocal Separation Quality:** The model has well isolated the singer's voice from the original recording.
2. **Vocal Leakage:** No vocal leakage in the No-Vocals output.
3. **Instrument Leakage:** No instrument leakage in the Vocals output.
4. **Accompaniment Quality:** The No-Vocals output sounds complete and natural as an accompaniment track.
5. **Audio Artifacts:** No distortion or unnatural sounds have been introduced by the separation process.
6. **Vocal Naturalness:** The separated vocals sound like a natural human performance.
7. **Instrument Preservation:** All the original instruments have been properly preserved in the No-Vocals output.
8. **Balance Between Vocals and Accompaniment:** The separation feels balanced between the two outputs.
9. **Overall Separation Quality:** Vocals and accompaniment are clear with no vocal or instrument leakage and no major artifacts. Vocals are natural and instruments are preserved. Overall, the outputs are usable.
10. **Additional Observations:** No additional observations.

## Cross-Recording Observations
The qualitative evaluation across the three Baul Geet recordings indicates that vocal separation was consistently strong, and noticeable vocal leakage was not observed. The accompaniment was generally preserved well without introducing major artifacts, ensuring the vocals remained natural. The main exception was significant Ektara leakage into the Vocals output observed specifically in BAUL_016. Therefore, the baseline performed well overall in this small qualitative sample, but instrument-specific leakage remains a limitation.
