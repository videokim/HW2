import os
import shutil
import uuid
from fastapi import UploadFile

def create_temp_dir(base_dir: str = "temp_storage") -> tuple[str, str]:
    """Creates an isolated temporary directory for a specific task."""
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(base_dir, task_id)
    os.makedirs(task_dir, exist_ok=True)
    return task_dir, task_id

def save_upload_file_tmp(upload_file: UploadFile, dest_dir: str) -> str:
    """Saves the uploaded file to disk and returns the safe path."""
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    if not file_ext:
        file_ext = ".wav" # Fallback if missing
        
    safe_filename = f"input{file_ext}"
    file_path = os.path.join(dest_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

def cleanup_dir(dir_path: str):
    """Deletes a directory and its contents."""
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except Exception:
            pass # Ignore errors during cleanup for simplicity
