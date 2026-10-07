# Introduction
Pandavani is a highly theatrical folk ballad tradition from Chhattisgarh that narrates tales from the ancient Indian epic, the Mahabharata. Unlike purely musical traditions, Pandavani is an intense synthesis of singing, spoken-word storytelling, and dramatic acting. For Music Information Retrieval (MIR) and computational audio analysis, this tradition provides a unique dataset characterized by extreme dynamic range, rapid tempo shifts, and the continuous blurring of lines between rhythmic speech and melodic singing.

# Historical Background
Originating among the tribal communities of Chhattisgarh (such as the Gonds and Pardhans), Pandavani was traditionally performed exclusively by men. The art form gained international prominence in the late 20th century when female artists, most notably Padma Vibhushan Teejan Bai, popularized the aggressive, standing *Kapadik* style. The narrative focuses heavily on the Pandavas, with Bhima often serving as the central heroic figure.

# Geographic Distribution
The tradition is heavily concentrated in the state of Chhattisgarh, with significant cultural overlap into neighboring regions of Madhya Pradesh, Odisha, and Andhra Pradesh.

# Cultural Context
Pandavani is performed at village festivals, religious gatherings, and increasingly on global concert stages. The lead performer (the *Ragi*) acts as a one-person theater, embodying multiple characters. The performance is interactive, often involving a secondary singer/instrumentalist (the *Hunkara*) who provides vocal affirmations (like "Haan!" or "Oh ho!") to drive the narrative forward.

# Musical Characteristics
- **Scale and Melody**: The melodic structures are relatively simple, repetitive, and chant-like. The primary function of the melody is to carry the heavy lyrical narrative rather than to showcase complex musical virtuosity or *Raga* grammar.
- **Rhythm**: The rhythmic structure is highly dynamic and completely subservient to the story. The tempo frequently shifts from slow, free-form spoken narration to rapid, intense, driving rhythmic crescendos during battle scenes or emotional peaks.
- **Form**: The structure alternates continuously between sung verses (set to a repetitive musical meter) and spoken prose explanations (delivered with rhythmic cadence).

# Vocal Characteristics
The singing style is extraordinarily robust, loud, and physically demanding. The vocalist employs dramatic pitch shifts, aggressive shouts, wide vibratos, and sudden stops to emphasize narrative action. The rapid transition between spoken dialogue, rhythmic chanting, and full-throated singing presents a significant challenge for standard voice-activity detection (VAD) algorithms.

# Instrument Inventory

| Instrument | Brief Description | Musical Role | Frequency of Occurrence | Expected Source Separation Difficulty |
| :--- | :--- | :--- | :--- | :--- |
| **Tambura (Tanpura)** | A customized plucked lute, often adorned with bells and peacock feathers. | Serves a dual purpose: provides rhythmic strumming and acts as a theatrical prop (e.g., a mace or a bow). | Very High (Essential) | **Medium**. The strumming is percussive rather than a continuous drone, making it distinct, but the attached bells introduce high-frequency noise. |
| **Harmonium** | A hand-pumped reed organ. | Provides the core melodic support and a continuous tonal reference for the singer. | Very High | **High**. Shadows the repetitive vocal melody closely, leading to harmonic overlap. |
| **Dholak** | A double-headed hand drum. | Provides the driving, aggressive rhythmic accompaniment during sung verses. | Very High | **High**. During narrative climaxes, the Dholak is played extremely fast and loud, creating dense transient masking. |
| **Manjira / Kartal** | Small cymbals or wooden clappers played by the chorus. | Maintains the tempo and adds bright accents. | High | **Medium**. Sharp, high-frequency transients that can bleed into vocal sibilance. |

# Audio Recording Characteristics
- **Live Ensemble Dynamics**: Almost all Pandavani recordings, even those captured in a studio, are recorded as live ensemble performances because the interactive nature of the storytelling requires the musicians and the lead singer to cue off each other in real-time.
- **Extreme Dynamic Range**: The recordings feature massive dynamic swings, from the quietest whisper during a spoken passage to explosive, clipping-prone shouts during a battle sequence.

# Source Separation Feasibility

## Vocal Separation
- **Expected Difficulty**: Moderate to Hard.
- **Technical Challenges**: The extreme dynamic range makes consistent vocal extraction difficult. Sudden shouts or spoken-word segments may be misclassified by standard vocal extraction models trained primarily on continuous singing. Furthermore, the vocal affirmations (*Hunkaras*) from the chorus bleed into the lead vocal stem.

## Individual Instrument Separation
- **Expected Difficulty**: Hard.
- **Technical Challenges**: The rapid, dense playing of the Dholak during climax sections creates a "wall of sound" that bleeds heavily into all other microphone channels. The Harmonium's repetitive drone also masks the lower fundamental frequencies of the vocalist.

# Recommendations for Dataset Curation
To ensure high-quality data for MIR and Raag origin analysis:
1. **Capture the Full Spectrum**: Ensure the dataset includes both the slow, spoken-word narrative sections and the fast, aggressive sung verses to capture the tradition's full dynamic and rhythmic range.
2. **Monitor Clipping**: Due to the aggressive nature of the singing, prioritize recordings where the transient peaks (shouts and Dholak slaps) have not been subjected to severe digital clipping or harsh limiting.
3. **Isolate the Tambura**: Pay special attention to the unique rhythmic strumming of the lead performer's Tambura, as it functions very differently from a classical drone Tanpura.

# References
- Vatsyayan, K. (1987). *Traditions of Indian Folk Dance*. Clarion Books.
- Tiwary, S. (2007). *Folk Theater of India*.
- Blackburn, S. H. (1986). *Performance Markers in an Indian Story-Type*.

## Project Notes
- **Why this tradition was selected**: Pandavani represents a unique blend of narrative storytelling (spoken word) and rhythmic singing (ballad). It provides a dataset rich in extreme dynamic variations, theatrical vocal delivery, and shifting tempos.
- **Most important instruments**: Tambura (as a rhythm/prop), Harmonium, Dholak, Manjira/Kartal.
- **Expected vocal separation difficulty**: Moderate to Hard (due to extreme dynamic range, shouts, and shifts between speech and song).
- **Expected individual instrument separation difficulty**: Hard (due to dense percussive crescendos and the inherent bleed of live-ensemble recordings).
