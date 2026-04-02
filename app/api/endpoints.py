import os
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from app.utils.file_helper import create_temp_dir, save_upload_file_tmp, cleanup_dir
from app.services.audio_processor import process_audio_to_midi_sync

router = APIRouter()

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac"}

@router.post("/convert", summary="오디오 파일을 MIDI로 변환합니다.")
async def convert_audio_to_midi(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="WAV 또는 MP3 파일 (최대 20MB)")
):
    # 1. Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {ALLOWED_EXTENSIONS}")

    # For Python 3.9+ / FastAPI modern versions `file.size` is typically available. 
    # Optional robust size check can be done via reading chunks, but we rely on file.size for brevity.
    if getattr(file, "size", 0) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max allowed is {MAX_FILE_SIZE_MB}MB")

    # 2. Setup processing directory
    # temp_storage must be at the project root relative to app where server is run
    base_temp_dir = os.path.join(os.getcwd(), "temp_storage")
    task_dir, task_id = create_temp_dir(base_temp_dir)
    
    try:
        # Save file synchronously (FastAPI runs this in a threadpool)
        saved_audio_path = save_upload_file_tmp(file, task_dir)
        
        # 3. Process the audio asynchronously using ProcessPoolExecutor
        loop = asyncio.get_running_loop()
        executor = request.app.state.executor
        
        # Wrap CPU-bound operation
        zip_path = await loop.run_in_executor(
            executor,
            process_audio_to_midi_sync,
            saved_audio_path,
            task_dir
        )
        
        # 4. Schedule cleanup of the directory AFTER the response is sent back
        background_tasks.add_task(cleanup_dir, task_dir)
        
        # 5. Return the file
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"separated_midi_{task_id}.zip"
        )
        
    except Exception as e:
        # Cleanup immediately if an error occurred before returning
        cleanup_dir(task_dir)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
