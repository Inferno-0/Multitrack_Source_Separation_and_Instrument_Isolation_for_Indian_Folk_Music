"""
Reusable utility functions for audio operations and metadata formatting.
"""

from pathlib import Path
from typing import List, Union


def format_duration(seconds: float) -> str:
    """
    Formats a duration in seconds into a human-readable string (HH:MM:SS.ms).

    Args:
        seconds: The duration in seconds.

    Returns:
        A formatted duration string.
    """
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{ms:03d}"


def get_audio_files(directory: Union[Path, str], extension: str = ".wav") -> List[Path]:
    """
    Discovers all audio files with a specific extension within a directory.

    Args:
        directory: The directory to search for audio files.
        extension: The file extension to look for (default: '.wav').

    Returns:
        A sorted list of Path objects corresponding to the discovered audio files.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    files = list(dir_path.glob(f"*{extension}"))
    return sorted(files)


def validate_audio_file(file_path: Union[Path, str]) -> bool:
    """
    Performs basic validation to check if an audio file exists and is not empty.

    Args:
        file_path: Path to the audio file.

    Returns:
        True if the file exists and is greater than 0 bytes, False otherwise.
    """
    path = Path(file_path)
    return path.exists() and path.is_file() and path.stat().st_size > 0
