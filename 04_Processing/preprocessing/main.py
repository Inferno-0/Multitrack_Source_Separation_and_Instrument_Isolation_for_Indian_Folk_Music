import time
import argparse
from pathlib import Path
from tqdm import tqdm

import config
from logger import setup_logging
import utils
import metadata
import validation
import convert_audio

def map_files_to_ids(m4a_files: list, song_ids: list, existing_mapping: dict, logger) -> dict:
    """
    Creates a mapping between Song_ID and M4A filename.
    Follows conservative mapping rules to avoid guessing incorrectly.
    """
    mapping = {}
    unmapped_files = []
    
    # Track which IDs have been mapped
    mapped_ids = set()
    
    # 1. First Pass: Use existing mapping from the excel sheet if present
    for song_id, raw_file in existing_mapping.items():
        if song_id in song_ids:
            # Find the actual M4A path that matches this raw_file string
            matched_path = next((f for f in m4a_files if f.name == raw_file), None)
            if matched_path:
                processed_name = f"{song_id}.wav"
                mapping[song_id] = {
                    "m4a_path": matched_path,
                    "raw_name": raw_file,
                    "processed_name": processed_name
                }
                mapped_ids.add(song_id)
                
    # Filter files that haven't been matched via existing mapping
    remaining_files = [f for f in m4a_files if f not in [m["m4a_path"] for m in mapping.values()]]
    remaining_ids = [s for s in song_ids if s not in mapped_ids]
    
    if remaining_ids:
        logger.warning(f"Found {len(remaining_ids)} Song_IDs missing a Raw_File_Name mapping in Excel. Skipping them.")
        for sid in remaining_ids:
            logger.warning(f"Unmapped Song_ID: {sid}")
            
    if remaining_files:
        logger.warning(f"Found {len(remaining_files)} M4A files not mapped to any Song_ID. Skipping them.")
        for f in remaining_files:
            logger.warning(f"Unmapped M4A File: {f.name}")
            
    return mapping

def process_dataset(tradition_dir: Path, logger) -> dict:
    """
    Processes a single tradition dataset.
    """
    logger.info(f"--- Processing Tradition: {tradition_dir.name} ---")
    
    stats = {
        "processed": 0,
        "skipped": 0,
        "converted": 0,
        "failed": 0,
        "verified": 0,
        "verify_failed": 0
    }
    
    m4a_files = utils.get_m4a_files(tradition_dir)
    excel_path = utils.get_metadata_file(tradition_dir)
    
    if not validation.validate_dataset_pre_conversion(m4a_files, excel_path):
        logger.error(f"Pre-conversion validation failed for {tradition_dir.name}. Terminating.")
        return stats
        
    if not excel_path:
        logger.error(f"Cannot proceed for {tradition_dir.name}: Metadata file missing.")
        return stats
        
    # Ensure columns exist
    if not metadata.create_missing_columns(excel_path):
        logger.error("Failed to prepare metadata columns.")
        return stats
        
    # Get IDs and existing mappings
    song_ids = metadata.get_all_song_ids(excel_path)
    existing_mapping = metadata.get_existing_mapping(excel_path)
    
    # Map files
    mapping = map_files_to_ids(m4a_files, song_ids, existing_mapping, logger)
    
    if not mapping or len(mapping) != len(m4a_files):
        logger.error(f"Strict mapping failure in {tradition_dir.name}. Halting.")
        return stats
        
    # Update Excel with new mappings before conversion
    excel_update_dict = {sid: (m["raw_name"], m["processed_name"]) for sid, m in mapping.items()}
    metadata.update_metadata(excel_path, excel_update_dict)
    
    output_dir = tradition_dir / "Audio" / "WAV"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Conversion Loop
    logger.info(f"Starting conversion for {len(mapping)} matched files in {tradition_dir.name}")
    
    # Use tqdm for progress bar
    with tqdm(total=len(mapping), desc=f"Converting {tradition_dir.name}", unit="file") as pbar:
        for song_id, m in mapping.items():
            m4a_path = m["m4a_path"]
            wav_path = output_dir / m["processed_name"]
            
            stats["processed"] += 1
            
            # Convert
            success = convert_audio.convert_audio(
                m4a_path, 
                wav_path, 
                sample_rate=config.SAMPLE_RATE,
                codec=config.AUDIO_CODEC,
                overwrite=config.OVERWRITE_WAV
            )
            
            if success:
                stats["converted"] += 1
                # Validate
                if config.VERIFY_AUDIO:
                    if validation.validate_audio(wav_path, config.SAMPLE_RATE, config.AUDIO_CODEC):
                        stats["verified"] += 1
                    else:
                        stats["verify_failed"] += 1
                        logger.error(f"Post-conversion verification failed for {wav_path.name}. Terminating.")
                        return stats
            else:
                stats["failed"] += 1
                logger.error(f"Conversion failed for {wav_path.name}. Terminating.")
                return stats
                
            pbar.update(1)
            
    return stats

def main():
    start_time = time.time()
    
    logger = setup_logging(config.LOG_FILENAME, config.GENERATE_LOG)
    logger.info("==================================================")
    logger.info("STARTED MIR PREPROCESSING PIPELINE")
    logger.info("==================================================")
    
    if not convert_audio.verify_ffmpeg():
        logger.error("FFmpeg verification failed. Halting execution.")
        return
        
    traditions = []
    if config.PROCESS_ALL:
        traditions = utils.get_tradition_folders(config.DATASET_ROOT)
        logger.info(f"PROCESS_ALL=True. Found {len(traditions)} tradition(s).")
    else:
        target = config.DATASET_ROOT / config.TRADITION
        if target.exists() and target.is_dir():
            traditions = [target]
        else:
            logger.error(f"Target tradition not found: {target}")
            
    if not traditions:
        logger.error("No valid traditions to process. Exiting.")
        return
        
    global_stats = {
        "processed": 0,
        "converted": 0,
        "failed": 0,
        "verified": 0,
        "verify_failed": 0
    }
    
    for tradition_dir in traditions:
        stats = process_dataset(tradition_dir, logger)
        for k in global_stats:
            global_stats[k] += stats.get(k, 0)
            
    elapsed = time.time() - start_time
    
    logger.info("==================================================")
    logger.info("PREPROCESSING PIPELINE SUMMARY")
    logger.info("==================================================")
    logger.info(f"Total Time Elapsed  : {elapsed:.2f} seconds")
    logger.info(f"Total Files Processed : {global_stats['processed']}")
    logger.info(f"Total Converted       : {global_stats['converted']}")
    logger.info(f"Total Failed          : {global_stats['failed']}")
    if config.VERIFY_AUDIO:
        logger.info(f"Total Verified OK     : {global_stats['verified']}")
        logger.info(f"Total Verify Failed   : {global_stats['verify_failed']}")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
