# backend/app/utils/audio.py
import subprocess
from pathlib import Path
from typing import Optional

def convert_to_wav(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Convert audio file to WAV format using ffmpeg.
    If output_path is None, creates a new file with .wav extension.

    Args:
        input_path: Path to input audio file
        output_path: Optional output path. If None, uses input_path with .wav extension

    Returns:
        Path to the converted WAV file
    """
    if output_path is None:
        output_path = input_path.with_suffix('.wav')

    # Check if input is already WAV
    if input_path.suffix.lower() == '.wav':
        return input_path

    try:
        # Convert to WAV using ffmpeg
        # -y: overwrite output file if exists
        # -i: input file
        # -ar 16000: sample rate 16kHz (commonly used for STT)
        # -ac 1: mono channel
        # -acodec pcm_s16le: PCM signed 16-bit little-endian
        subprocess.run([
            'ffmpeg',
            '-y',
            '-i', str(input_path),
            '-ar', '16000',
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            str(output_path)
        ], check=True, capture_output=True)

        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to convert audio file: {e.stderr.decode()}")
    except FileNotFoundError:
        # ffmpeg not installed - return original file and let the API handle it
        print("Warning: ffmpeg not found. Skipping audio conversion.")
        return input_path

def validate_audio_file(file_path: Path, max_size: int = 50 * 1024 * 1024) -> bool:
    """
    Validate audio file size and format.

    Args:
        file_path: Path to audio file
        max_size: Maximum file size in bytes (default 50MB)

    Returns:
        True if valid, False otherwise
    """
    if not file_path.exists():
        return False

    if file_path.stat().st_size > max_size:
        return False

    return True
