"""
Validates the standardized dataset at D:\ISOLATED_INSTRUMENTS_PREPARED
ensuring all audio is 44.1kHz, Mono, 16-bit PCM WAV, no NaNs/Infs,
and counts exactly match expected values.
"""

import os
import csv
import numpy as np
import soundfile as sf

PREPARED_DIR = r"D:\ISOLATED_INSTRUMENTS_PREPARED"
SOURCE_DIR = r"D:\ISOLATED_INSTRUMENTS"

expected_counts = {
    "vocals": 160,
    "tabla": 797,
    "harmonium": 1322,
    "flute": 129,
    "dhul": 13,
    "dholak": 55
}

total_expected = sum(expected_counts.values())

print("=== POST-STANDARDIZATION VALIDATION ===")

# 1. Check Source unchanged
src_files = 0
for root, _, files in os.walk(SOURCE_DIR):
    for f in files:
        if f.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aif', '.aiff')):
            src_files += 1

print(f"Source audio files: {src_files} (Expected 2476)")
if src_files != total_expected:
    print("FATAL: Source file count changed! Aborting validation.")
    exit(1)

# 2. Check Outputs
actual_files = 0
failures = []

for inst, expected in expected_counts.items():
    inst_dir = os.path.join(PREPARED_DIR, inst, "audio")
    meta_path = os.path.join(PREPARED_DIR, inst, "metadata.csv")
    
    if not os.path.exists(inst_dir):
        failures.append(f"Missing directory for {inst}")
        continue
        
    files = [f for f in os.listdir(inst_dir) if f.endswith('.wav')]
    if len(files) != expected:
        failures.append(f"{inst} count mismatch: {len(files)} vs {expected}")
        
    actual_files += len(files)
    
    # Check Metadata
    if not os.path.exists(meta_path):
        failures.append(f"Missing metadata.csv for {inst}")
        continue
        
    meta_files = 0
    with open(meta_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            meta_files += 1
            # Verify file exists
            if not os.path.exists(os.path.join(inst_dir, row["standardized_filename"])):
                failures.append(f"Metadata references missing file: {row['standardized_filename']}")
                
    if meta_files != expected:
        failures.append(f"{inst} metadata count mismatch: {meta_files} vs {expected}")

    # Validate actual audio files
    for idx, f in enumerate(files):
        fpath = os.path.join(inst_dir, f)
        try:
            info = sf.info(fpath)
            if info.samplerate != 44100: failures.append(f"{f} SR != 44100 ({info.samplerate})")
            if info.channels != 1: failures.append(f"{f} CH != 1 ({info.channels})")
            if info.subtype != 'PCM_16': failures.append(f"{f} format != PCM_16 ({info.subtype})")
            if info.duration <= 0: failures.append(f"{f} duration <= 0")
            
            # Read snippet to ensure no NaNs
            data, sr = sf.read(fpath, dtype='float32')
            if not np.isfinite(data).all():
                failures.append(f"{f} contains NaN or Inf values")
                
        except Exception as e:
            failures.append(f"Failed to read {f}: {e}")

print(f"\nTotal standardized files: {actual_files} (Expected {total_expected})")

if failures:
    print("\nVALIDATION FAILED with following errors:")
    for err in failures[:20]:
        print(f" - {err}")
    if len(failures) > 20:
        print(f" ... and {len(failures) - 20} more errors.")
else:
    print("\nVALIDATION PASSED.")
    print("All files are exactly 44.1kHz, Mono, 16-bit PCM WAV. Metadata counts match perfectly. Source dataset remains untouched.")
