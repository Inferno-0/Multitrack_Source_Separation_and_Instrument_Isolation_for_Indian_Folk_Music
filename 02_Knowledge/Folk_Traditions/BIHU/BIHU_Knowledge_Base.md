# Introduction
Bihu music is the core traditional folk music of Assam, typically performed during the Bihu festivals (especially Rongali Bihu). It is characterized by its energetic rhythm, vibrant vocal expressions, and close association with agriculture and springtime celebrations. For Music Information Retrieval (MIR) and computational analysis, Bihu presents an interesting challenge due to its polyrhythmic percussion, distinct melodic scales, and dynamic interplay between male and female vocals.

# Historical Background
Bihu music has its roots in the agrarian society of the Brahmaputra Valley, evolving from ancient fertility cults and agricultural rites. Historically, it was performed in fields or under trees (Husori) and later transitioned into more structured community performances. The music carries the socio-cultural narrative of the Assamese people, merging indigenous tribal traditions with Indo-Aryan influences over centuries.

# Geographic Distribution
The tradition is primarily distributed across the Indian state of Assam. While Upper Assam is considered the heartland of the purest acoustic Bihu forms, variations exist across Lower Assam and the Barak Valley. Regional nuances exist in the phrasing and dialect, though the core rhythmic structures remain universally consistent across the state.

# Cultural Context
Bihu is inextricably linked to the Assamese identity. It is non-religious in its purest form, celebrating nature, youth, love, and the harvest cycle. Songs (Bihu Geet) often feature romantic or nature-inspired themes. Performance involves communal dancing, rapid tempo shifts, and call-and-response vocal structures that require precise synchronization between the lead singer, the chorus, and the percussionists.

# Musical Characteristics
- **Scale and Melody**: Bihu melodies are predominantly pentatonic, closely resembling the major pentatonic scale but with distinct microtonal variations (shruti). 
- **Rhythm**: Highly syncopated and polyrhythmic. The base tempo is usually upbeat, starting moderately and accelerating toward the climax. The meter is often in 4/4 or 2/4 but with complex internal subdivisions.
- **Form**: Typically features a strophic form with a repetitive chorus and improvisational verses. 

# Vocal Characteristics
Bihu vocals are energetic, bright, and open-throated. There is a strong emphasis on high registers and dynamic leaps. The tradition utilizes both solo lead singing and unison choral responses. Vocal embellishments are rhythmic rather than highly melismatic, matching the percussive drive of the instruments. 

# Instrument Inventory

## Dhol (Barrel Drum)
- **Description**: A double-headed barrel drum played with a stick on one side and a bare hand on the other. 
- **Musical Role**: The rhythmic backbone of Bihu. It dictates the tempo, complex polyrhythms, and structural shifts.
- **Typical Usage**: Constant, driving percussive patterns.
- **Expected Difficulty of Source Separation**: **High**. The Dhol's wide frequency range (deep bass and sharp transients) overlaps significantly with vocals and other percussion, making clean extraction difficult.

## Pepa (Horn)
- **Description**: A wind instrument made from buffalo horn, possessing a high-pitched, piercing, and reedy tone.
- **Musical Role**: Provides sharp, melodic interludes and high-frequency counter-melodies.
- **Typical Usage**: Used in bursts during instrumental breaks; rarely plays simultaneously with the lead vocal.
- **Expected Difficulty of Source Separation**: **Medium**. Its distinct timbral footprint and high frequency make it easier to isolate, though it may bleed into high-frequency vocal harmonics.

## Gogona (Jaw Harp)
- **Description**: A bamboo jaw harp played by plucking a flexible reed against the mouth.
- **Musical Role**: Adds a buzzing, rhythmic drone and subtle percussive texture.
- **Typical Usage**: Continuous rhythmic support.
- **Expected Difficulty of Source Separation**: **High**. Its low amplitude and noisy, broad-spectrum buzz blend heavily with the Dhol and background noise.

## Taal (Cymbals)
- **Description**: Small to medium-sized bronze cymbals.
- **Musical Role**: Provides high-frequency rhythmic subdivision and time-keeping.
- **Typical Usage**: Constant striking to maintain the subdivision of the beat.
- **Expected Difficulty of Source Separation**: **Medium-High**. The broadband transient splash of cymbals is notoriously difficult to fully separate from the sharp attacks of the Dhol stick.

# Audio Recording Characteristics
Publicly available recordings of Bihu music vary wildly in quality. 
- **Live/Field Recordings**: Often suffer from poor microphone placement, wind noise, crowd chatter, and extreme clipping due to the loud volume of the Dhol.
- **Studio Recordings**: Tend to be heavily compressed with artificial reverb applied. Modern tracks often introduce electronic instruments (synthesizers, drum machines) which must be filtered out when curating datasets for traditional MIR tasks.
- **Spatialization**: Older recordings are predominantly mono, while modern recordings may have hard-panned stereo mixes.

# Source Separation Feasibility

## Vocal Separation
- **Expected Difficulty**: Moderate to Hard. 
- **Technical Challenges**: The sharp, high-amplitude transients of the Dhol and Taal often leak into the vocal frequencies. The energetic, open-throated singing style can share harmonic space with the Pepa. Current pre-trained models (like Spleeter or HTDemucs) trained on Western pop music will likely struggle with the unique percussive transients of the Dhol, occasionally misclassifying them as vocal plosives or artifacts.

## Individual Instrument Separation
- **Expected Difficulty**: Very Hard.
- **Technical Challenges**: Separating the Dhol from the Taal is a major challenge due to overlapping transient attacks. The Gogona is almost impossible to cleanly extract from a dense mix due to its low volume and broadband noise characteristics. Separation models will need to be fine-tuned specifically on isolated stems of Assamese folk instruments to achieve research-grade results.

# Recommendations for Dataset Curation
For building a high-quality dataset for Raag origin analysis and MIR:
1. **Prefer Acoustic Recordings**: Avoid modern, synthesized "Bihu Pop" tracks. Focus on recordings featuring only traditional acoustic instruments (Dhol, Pepa, Taal, Gogona, Baanhi).
2. **Seek Dry Mixes**: Recordings with minimal artificial reverb are preferred, as heavy reverb severely degrades pitch tracking and source separation performance.
3. **Clear Melodic Lines**: For Raag analysis, tracks with long, clear vocal phrasing and minimal instrumental masking are most valuable.
4. **Avoid Heavy Clipping**: Due to the percussive nature of the music, clipping is common. Curators should discard tracks where distortion masks the fundamental frequencies of the vocals.
