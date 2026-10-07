import subprocess
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict

from logger import logger
import metadata

def validate_dataset_pre_conversion(m4a_files: List[Path], excel_path: Path) -> bool:
    """
    Validates duplicate names and missing files before starting conversion.
    
    Args:
        m4a_files (List[Path]): List of M4A files in the dataset.
        excel_path (Path): Path to the metadata Excel file.
        
    Returns:
        bool: True if dataset passes soft validation (proceeds even with warnings).
    """
    valid = True
    
    # Check for missing M4A files completely
    if not m4a_files:
        logger.error("No M4A files found in the dataset.")
        valid = False
        
    # Check for duplicate raw file names in directory
    file_names = [f.name for f in m4a_files]
    duplicates = [item for item, count in Counter(file_names).items() if count > 1]
    if duplicates:
        logger.error(f"Duplicate M4A filenames found: {duplicates}")
        valid = False
        
    # Check Excel validation
    if not excel_path or not excel_path.exists():
        logger.error("Metadata Excel file is missing.")
        valid = False
    else:
        song_ids = metadata.get_all_song_ids(excel_path)
        if not song_ids:
            logger.error("No Song_IDs found in the metadata file.")
            valid = False
            
        duplicate_ids = [item for item, count in Counter(song_ids).items() if count > 1]
        if duplicate_ids:
            logger.error(f"Duplicate Song_IDs found in metadata: {duplicate_ids}")
            valid = False
            
        # Check existing mapping for duplicate or missing Raw_File_Name
        existing_mapping = metadata.get_existing_mapping(excel_path)
        raw_names_in_excel = list(existing_mapping.values())
        duplicate_raws = [item for item, count in Counter(raw_names_in_excel).items() if count > 1]
        if duplicate_raws:
            logger.error(f"Duplicate Raw_File_Names found in metadata: {duplicate_raws}")
            valid = False
            
        # Ensure every Song_ID has a Raw_File_Name
        if len(existing_mapping) != len(song_ids):
            logger.error("Some Song_IDs are missing Raw_File_Name in the metadata.")
            valid = False
            
        # Check if every Raw_File_Name has a matching M4A
        for raw_name in raw_names_in_excel:
            if raw_name not in file_names:
                logger.error(f"Missing M4A file for Raw_File_Name: {raw_name}")
                valid = False
                
        # Check if there are extra M4A files without a metadata row
        for file_name in file_names:
            if file_name not in raw_names_in_excel:
                logger.error(f"Extra M4A file found without metadata record: {file_name}")
                valid = False
                
    return valid

def validate_audio(wav_path: Path, expected_sample_rate: int = 44100, expected_codec: str = "pcm_s16le") -> bool:
    """
    Uses FFprobe to verify that the generated WAV file is readable, not corrupted,
    and matches the target sample rate and codec.
    
    Args:
        wav_path (Path): Path to the generated WAV file.
        expected_sample_rate (int): The target sample rate.
        expected_codec (str): The target audio codec.
        
    Returns:
        bool: True if validation passes, False otherwise.
    """
    if not wav_path.exists():
        logger.error(f"Post-validation failed: File does not exist - {wav_path.name}")
        return False
        
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate",
        "-of", "json",
        str(wav_path)
    ]
    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"FFprobe failed to read file (possible corruption): {wav_path.name}")
            return False
            
        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])
        
        if not streams:
            logger.error(f"No audio stream found in {wav_path.name}")
            return False
            
        stream = streams[0]
        actual_codec = stream.get("codec_name")
        actual_sample_rate = int(stream.get("sample_rate", 0))
        
        if actual_codec != expected_codec:
            logger.error(f"Codec mismatch in {wav_path.name}: Expected {expected_codec}, got {actual_codec}")
            return False
            
        if actual_sample_rate != expected_sample_rate:
            logger.error(f"Sample rate mismatch in {wav_path.name}: Expected {expected_sample_rate}, got {actual_sample_rate}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Exception during FFprobe validation for {wav_path.name}: {e}")
        return False
