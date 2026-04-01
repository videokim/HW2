import os
import logging
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

logger = logging.getLogger(__name__)

def process_audio_to_midi_sync(audio_path: str, output_dir: str) -> str:
    """
    CPU-bound function that converts an audio file to MIDI.
    Designed to be executed in a ProcessPoolExecutor to avoid blocking the Event Loop.
    """
    try:
        logger.info(f"Starting MIDI conversion for: {audio_path}")
        
        predict_and_save(
            audio_path_list=[audio_path],
            output_directory=output_dir,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False,
            model_or_model_path=str(ICASSP_2022_MODEL_PATH) + ".tflite"
        )
        
        # Predict the output filename based on basic_pitch naming convention
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        expected_midi_name = f"{base_name}_basic_pitch.mid"
        midi_path = os.path.join(output_dir, expected_midi_name)
        
        if os.path.exists(midi_path):
            logger.info(f"MIDI conversion successful. Saved at: {midi_path}")
            return midi_path
        else:
            raise FileNotFoundError(f"Expected MIDI file not found: {midi_path}")
            
    except Exception as e:
        logger.error(f"Error during audio processing: {e}")
        raise e
