import logging
from pathlib import Path
import pandas as pd
import openpyxl

# ======================================================================
# CONFIGURATION
# ======================================================================

DATASET_ROOT = Path("../../03_Datasets").resolve()
MASTER_TRADITION = "BIHU"
REMOVE_EXTRA_COLUMNS = False

# ======================================================================
# LOGGING SETUP
# ======================================================================

def setup_logger() -> logging.Logger:
    """Configures the logger to output to both console and a file."""
    logger = logging.getLogger("propagate_schema")
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    fh = logging.FileHandler("schema_propagation.log", mode='w', encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger

logger = setup_logger()

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def get_master_schema(dataset_root: Path, master_tradition: str) -> list[str]:
    """
    Reads the master metadata file and extracts the column headers.
    
    Args:
        dataset_root (Path): Root directory for datasets.
        master_tradition (str): Name of the master tradition.
        
    Returns:
        list[str]: Ordered list of master column names.
    """
    master_dir = dataset_root / master_tradition / "Metadata"
    if not master_dir.exists():
        logger.error(f"Master tradition metadata directory not found: {master_dir}")
        return []
        
    master_file = None
    for f in master_dir.iterdir():
        if f.suffix.lower() == ".xlsx" and not f.name.startswith("~$"):
            master_file = f
            break
            
    if not master_file:
        logger.error(f"No master Excel file found in {master_dir}")
        return []
        
    try:
        # Read just the header
        df_master = pd.read_excel(master_file, engine='openpyxl', nrows=0)
        schema = list(df_master.columns)
        logger.info(f"Loaded master schema from {master_file.name} with {len(schema)} columns.")
        return schema
    except Exception as e:
        logger.error(f"Failed to read master schema: {e}")
        return []

def propagate_schema_to_file(
    target_file: Path, 
    master_schema: list[str], 
    remove_extra: bool
) -> dict:
    """
    Updates a target metadata Excel file to match the master schema structure.
    
    Args:
        target_file (Path): Path to the target metadata.xlsx.
        master_schema (list[str]): Ordered list of columns from the master template.
        remove_extra (bool): Whether to remove columns not present in master.
        
    Returns:
        dict: Statistics about the operation on this file.
    """
    stats = {
        "added": [],
        "removed": [],
        "reordered": False,
        "error": None
    }
    
    try:
        # Read the entire target excel file
        df = pd.read_excel(target_file, engine='openpyxl')
        original_cols = list(df.columns)
        
        # 1. Add missing columns with empty values
        for col in master_schema:
            if col not in original_cols:
                df[col] = pd.NA
                stats["added"].append(col)
                
        # 2. Determine columns to keep
        if remove_extra:
            cols_to_keep = [col for col in master_schema]
            for col in original_cols:
                if col not in master_schema:
                    stats["removed"].append(col)
        else:
            # Keep all master columns in order, then append any extra original columns
            cols_to_keep = [col for col in master_schema]
            for col in original_cols:
                if col not in master_schema:
                    cols_to_keep.append(col)
                    
        # 3. Check if reordering is necessary
        if list(df.columns) != cols_to_keep:
            df = df[cols_to_keep]
            if not stats["added"] and not stats["removed"]:
                stats["reordered"] = True
                
        # 4. Save if any changes occurred
        if stats["added"] or stats["removed"] or stats["reordered"] or list(original_cols) != cols_to_keep:
            df.to_excel(target_file, index=False, engine='openpyxl')
            logger.info(f"Updated {target_file.parent.parent.name}/{target_file.name}: "
                        f"Added {len(stats['added'])}, Removed {len(stats['removed'])}, Reordered: {stats['reordered']}")
        else:
            logger.info(f"Skipped {target_file.parent.parent.name}/{target_file.name} (already matches schema).")
            
        return stats
    except Exception as e:
        logger.error(f"Error processing {target_file}: {e}")
        stats["error"] = str(e)
        return stats

def main():
    logger.info("==================================================")
    logger.info("STARTED METADATA SCHEMA PROPAGATION")
    logger.info("==================================================")
    
    master_schema = get_master_schema(DATASET_ROOT, MASTER_TRADITION)
    if not master_schema:
        logger.error("Failed to extract master schema. Halting execution.")
        return
        
    # Validation per prompt: ensure critical columns exist in master schema
    critical_columns = ["Song_ID", "Raw_File_Name", "Processed_File_Name"]
    missing_critical = [col for col in critical_columns if col not in master_schema]
    if missing_critical:
        logger.error(f"Master schema is missing critical columns: {missing_critical}. Halting.")
        return
        
    # Iterate through all traditions
    updated_count = 0
    skipped_count = 0
    error_count = 0
    total_added = 0
    
    for tradition_dir in DATASET_ROOT.iterdir():
        if not tradition_dir.is_dir() or tradition_dir.name.startswith("."):
            continue
            
        if tradition_dir.name == MASTER_TRADITION:
            continue
            
        metadata_dir = tradition_dir / "Metadata"
        if not metadata_dir.exists():
            continue
            
        # Find the metadata excel file
        target_file = None
        for f in metadata_dir.iterdir():
            if f.suffix.lower() == ".xlsx" and not f.name.startswith("~$"):
                target_file = f
                break
                
        if not target_file:
            logger.warning(f"No metadata file found for tradition {tradition_dir.name}. Skipping.")
            continue
            
        # Propagate schema
        stats = propagate_schema_to_file(target_file, master_schema, REMOVE_EXTRA_COLUMNS)
        
        if stats["error"]:
            error_count += 1
        elif stats["added"] or stats["removed"] or stats["reordered"]:
            updated_count += 1
            total_added += len(stats["added"])
        else:
            skipped_count += 1
            
    logger.info("==================================================")
    logger.info("SCHEMA PROPAGATION REPORT")
    logger.info("==================================================")
    logger.info(f"Traditions Updated : {updated_count}")
    logger.info(f"Columns Added      : {total_added}")
    logger.info(f"Traditions Skipped : {skipped_count} (Already up to date)")
    logger.info(f"Errors Encountered : {error_count}")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
