import os
from pathlib import Path
from typing import List

from logger import logger

def get_tradition_folders(dataset_root: Path) -> List[Path]:
    """
    Scans the dataset root and returns a list of tradition directories.
    
    Args:
        dataset_root (Path): Path to the 03_Datasets folder.
        
    Returns:
        List[Path]: A list of Path objects for each valid tradition folder.
    """
    if not dataset_root.exists() or not dataset_root.is_dir():
        logger.error(f"Dataset root does not exist: {dataset_root}")
        return []
    
    traditions = []
    for item in dataset_root.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Ensure it has the expected structure (Audio and Metadata)
            if (item / "Audio" / "M4A").exists() and (item / "Metadata").exists():
                traditions.append(item)
                
    return sorted(traditions)

def get_m4a_files(tradition_dir: Path) -> List[Path]:
    """
    Finds all M4A files in the given tradition's Audio/M4A/ directory.
    
    Args:
        tradition_dir (Path): Path to the specific tradition directory.
        
    Returns:
        List[Path]: A sorted list of M4A files.
    """
    m4a_dir = tradition_dir / "Audio" / "M4A"
    if not m4a_dir.exists():
        logger.warning(f"M4A directory not found: {m4a_dir}")
        return []
    
    return sorted([f for f in m4a_dir.iterdir() if f.suffix.lower() == ".m4a"])

def get_metadata_file(tradition_dir: Path) -> Path:
    """
    Finds the metadata excel file in the given tradition's Metadata/ directory.
    If multiple exist, returns the first one matching *.xlsx, or metadata.xlsx.
    
    Args:
        tradition_dir (Path): Path to the specific tradition directory.
        
    Returns:
        Path: Path to the Excel file, or None if not found.
    """
    metadata_dir = tradition_dir / "Metadata"
    if not metadata_dir.exists():
        return None
    
    expected_file = metadata_dir / "metadata.xlsx"
    if expected_file.exists() and expected_file.is_file():
        return expected_file
    
    return None
