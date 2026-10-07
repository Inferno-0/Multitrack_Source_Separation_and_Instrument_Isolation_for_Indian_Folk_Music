from pathlib import Path

# ======================================================================
# CONFIGURATION
# ======================================================================

# Root directory containing the datasets (relative to the project root or absolute)
DATASET_ROOT = Path("../../03_Datasets").resolve()

# Target tradition to process if PROCESS_ALL is False
TRADITION = "YAKSHAGANA"

# Set to True to process all traditions inside DATASET_ROOT
PROCESS_ALL = False

# Audio Settings
SAMPLE_RATE = 44100
BIT_DEPTH = 16
AUDIO_CODEC = "pcm_s16le"

# Overwrite existing WAV files in Audio/WAV/
OVERWRITE_WAV = False

# Verify the output audio file after conversion
VERIFY_AUDIO = True

# Logging Settings
GENERATE_LOG = True
LOG_FILENAME = "conversion.log"
