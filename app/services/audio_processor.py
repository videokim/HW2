import os
import logging
import subprocess
import zipfile
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

logger = logging.getLogger(__name__)

def process_audio_to_midi_sync(audio_path: str, task_dir: str) -> str:
    """
    CPU-bound function that separates audio using Demucs and converts to MIDI.
    Designed to be executed in a ProcessPoolExecutor to avoid blocking the Event Loop.
    """
    try:
        logger.info(f"Starting Demucs source separation for: {audio_path}")
        
        # Demucs output structure: task_dir/htdemucs/{base_name}/
        # Using capture_output to prevent flooding console, but raise on error
        subprocess.run(
            ["demucs", "-n", "htdemucs", "-o", task_dir, audio_path], 
            check=True,
            capture_output=True
        )
        
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        demucs_out_dir = os.path.join(task_dir, "htdemucs", base_name)
        
        if not os.path.exists(demucs_out_dir):
            raise FileNotFoundError("Demucs output directory not found.")
            
        # Get all 4 separated stems
        stems = ["vocals.wav", "bass.wav", "drums.wav", "other.wav"]
        stem_paths = [os.path.join(demucs_out_dir, stem) for stem in stems]
        valid_stems = [p for p in stem_paths if os.path.exists(p)]
        
        logger.info(f"Starting MIDI conversion for stems: {valid_stems}")
        
        # basic-pitch converts list of files sequentially
        predict_and_save(
            audio_path_list=valid_stems,
            output_directory=demucs_out_dir,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False,
            model_or_model_path=str(ICASSP_2022_MODEL_PATH) + ".tflite"
        )
        
        # Zip all results together
        zip_path = os.path.join(task_dir, f"result_separated.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(demucs_out_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create nice relative paths inside ZIP
                    arcname = os.path.relpath(file_path, demucs_out_dir)
                    zipf.write(file_path, arcname)
                    
        logger.info(f"Zipped all separated files and MIDIs into {zip_path}")
        return zip_path
            
    except Exception as e:
        logger.error(f"Error during audio processing: {e}")
        raise e
