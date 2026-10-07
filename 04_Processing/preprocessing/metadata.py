import pandas as pd
import openpyxl
from pathlib import Path
from typing import Dict, List, Tuple

from logger import logger

def create_missing_columns(excel_path: Path) -> bool:
    """
    Ensures 'Raw_File_Name' and 'Processed_File_Name' exist immediately after 'Song_ID'.
    Preserves existing data and formatting by using openpyxl.
    
    Args:
        excel_path (Path): Path to the metadata Excel file.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        
        # Find the column index of Song_ID
        header_row = 1
        song_id_col = -1
        raw_file_col = -1
        processed_file_col = -1
        
        for cell in ws[header_row]:
            if cell.value == "Song_ID":
                song_id_col = cell.column
            elif cell.value == "Raw_File_Name":
                raw_file_col = cell.column
            elif cell.value == "Processed_File_Name":
                processed_file_col = cell.column
                
        if song_id_col == -1:
            logger.error(f"Missing 'Song_ID' column in {excel_path.name}")
            return False
            
        columns_modified = False
        
        # If Raw_File_Name doesn't exist, insert it right after Song_ID
        if raw_file_col == -1:
            ws.insert_cols(song_id_col + 1)
            ws.cell(row=header_row, column=song_id_col + 1).value = "Raw_File_Name"
            columns_modified = True
            
        # Refresh header indices
        raw_file_col = -1
        for cell in ws[header_row]:
            if cell.value == "Raw_File_Name":
                raw_file_col = cell.column
                
        # If Processed_File_Name doesn't exist, insert it right after Raw_File_Name
        if processed_file_col == -1 and raw_file_col != -1:
            ws.insert_cols(raw_file_col + 1)
            ws.cell(row=header_row, column=raw_file_col + 1).value = "Processed_File_Name"
            columns_modified = True
            
        if columns_modified:
            wb.save(excel_path)
            logger.info(f"Added missing metadata columns in {excel_path.name}")
            
        wb.close()
        return True
    except Exception as e:
        logger.error(f"Failed to modify columns in {excel_path.name}: {e}")
        return False

def update_metadata(excel_path: Path, mapping: Dict[str, Tuple[str, str]]) -> bool:
    """
    Updates the metadata with Raw_File_Name and Processed_File_Name based on Song_ID.
    
    Args:
        excel_path (Path): Path to the metadata Excel file.
        mapping (Dict[str, Tuple[str, str]]): Dictionary mapping Song_ID to (Raw_File_Name, Processed_File_Name).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        
        header = {cell.value: cell.column for cell in ws[1]}
        
        if "Song_ID" not in header or "Raw_File_Name" not in header or "Processed_File_Name" not in header:
            logger.error(f"Required columns missing in {excel_path.name} before update.")
            return False
            
        updates = 0
        for row in range(2, ws.max_row + 1):
            song_id_cell = ws.cell(row=row, column=header["Song_ID"])
            song_id = song_id_cell.value
            
            if song_id and song_id in mapping:
                raw_name, processed_name = mapping[song_id]
                
                raw_cell = ws.cell(row=row, column=header["Raw_File_Name"])
                processed_cell = ws.cell(row=row, column=header["Processed_File_Name"])
                
                # Only update if empty to prevent accidental overwrites
                if not raw_cell.value:
                    raw_cell.value = raw_name
                    updates += 1
                if not processed_cell.value:
                    processed_cell.value = processed_name
                    updates += 1
                    
        if updates > 0:
            wb.save(excel_path)
            logger.info(f"Updated metadata mapping for {updates} records in {excel_path.name}")
            
        wb.close()
        return True
    except Exception as e:
        logger.error(f"Failed to update metadata in {excel_path.name}: {e}")
        return False

def get_existing_mapping(excel_path: Path) -> Dict[str, str]:
    """
    Extracts the existing mapping of Song_ID to Raw_File_Name.
    
    Args:
        excel_path (Path): Path to the metadata Excel file.
        
    Returns:
        Dict[str, str]: Mapping of Song_ID to Raw_File_Name.
    """
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
        if "Song_ID" not in df.columns or "Raw_File_Name" not in df.columns:
            return {}
            
        # Drop rows where Song_ID or Raw_File_Name is NaN
        df_valid = df.dropna(subset=["Song_ID", "Raw_File_Name"])
        return dict(zip(df_valid["Song_ID"].astype(str), df_valid["Raw_File_Name"].astype(str)))
    except Exception as e:
        logger.error(f"Failed to read existing mapping from {excel_path.name}: {e}")
        return {}

def get_all_song_ids(excel_path: Path) -> List[str]:
    """
    Returns all Song_IDs from the excel file.
    
    Args:
        excel_path (Path): Path to the metadata Excel file.
        
    Returns:
        List[str]: List of Song_IDs.
    """
    try:
        df = pd.read_excel(excel_path, engine="openpyxl")
        if "Song_ID" not in df.columns:
            return []
        
        return df["Song_ID"].dropna().astype(str).tolist()
    except Exception as e:
        logger.error(f"Failed to read Song_IDs from {excel_path.name}: {e}")
        return []
