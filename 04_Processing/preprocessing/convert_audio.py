import subprocess
from pathlib import Path

from logger import logger

def verify_ffmpeg() -> bool:
    """
    Checks if FFmpeg and FFprobe are installed and available in the system PATH.
    
    Returns:
        bool: True if installed, False otherwise.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        subprocess.run(
            ["ffprobe", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg or FFprobe is not installed or not in the system PATH.")
        return False

def convert_audio(
    input_m4a: Path, 
    output_wav: Path, 
    sample_rate: int = 44100, 
    codec: str = "pcm_s16le",
    overwrite: bool = False
) -> bool:
    """
    Converts an M4A file to WAV using FFmpeg without modifying content (just transcode).
    
    Args:
        input_m4a (Path): Path to the source M4A file.
        output_wav (Path): Path where the WAV should be saved.
        sample_rate (int): Target sample rate. Defaults to 44100.
        codec (str): Target audio codec. Defaults to 'pcm_s16le'.
        overwrite (bool): If True, overwrites existing WAV file.
        
    Returns:
        bool: True if conversion succeeds, False otherwise.
    """
    if not input_m4a.exists():
        logger.error(f"Input file does not exist: {input_m4a.name}")
        return False
        
    if output_wav.exists() and not overwrite:
        logger.info(f"Skipping existing file (OVERWRITE_WAV=False): {output_wav.name}")
        return True

    # Ensure output directory exists
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    
    command = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-i", str(input_m4a),
        "-c:a", codec,
        "-ar", str(sample_rate),
        # Remove any loudness normalization, silence trimming or other filters
        "-af", "aresample=resampler=soxr", # high quality resampler just in case
        str(output_wav)
    ]
    
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"FFmpeg conversion failed for {input_m4a.name}: {result.stderr}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Failed to execute FFmpeg for {input_m4a.name}: {e}")
        return False
