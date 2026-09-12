"""
Audio Processor Module
Handles audio file processing and conversion
"""

import os
import logging
from pathlib import Path
import asyncio
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Process and convert audio files"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.supported_formats = ["mp3", "wav", "ogg", "flac", "m4a", "aac"]
        logger.info("🎵 Audio processor initialized")
    
    @staticmethod
    def get_file_format(file_path: str) -> Optional[str]:
        """Get file format from path"""
        try:
            file_ext = Path(file_path).suffix.lower().strip(".")
            return file_ext if file_ext else None
        except Exception as e:
            logger.error(f"❌ Error getting file format: {e}")
            return None
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting file size: {e}")
            return None
    
    def is_valid_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_format = self.get_file_format(file_path)
        
        if not file_format:
            logger.warning(f"⚠️ Could not determine file format: {file_path}")
            return False
        
        is_valid = file_format.lower() in self.supported_formats
        
        if not is_valid:
            logger.warning(f"⚠️ Unsupported format: {file_format}")
        
        return is_valid
    
    @staticmethod
    async def convert_to_wav(input_path: str, output_path: str) -> bool:
        """Convert audio file to WAV format using ffmpeg"""
        try:
            # Check if ffmpeg is installed
            import subprocess
            
            command = [
                "ffmpeg",
                "-i", input_path,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-q:a", "0",
                "-map", "a",
                output_path,
                "-y"  # Overwrite output file
            ]
            
            # Run ffmpeg command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Converted to WAV: {output_path}")
                return True
            else:
                logger.error(f"❌ FFmpeg conversion failed: {stderr.decode()}")
                return False
        
        except FileNotFoundError:
            logger.warning("⚠️ FFmpeg not installed. Using raw audio file.")
            return False
        except Exception as e:
            logger.error(f"❌ Error converting audio: {e}")
            return False
    
    @staticmethod
    async def extract_audio_info(file_path: str) -> Dict[str, Any]:
        """Extract audio information using ffprobe"""
        try:
            import subprocess
            
            command = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                info = json.loads(stdout.decode())
                logger.info(f"✅ Extracted audio info from: {file_path}")
                return info
            else:
                logger.warning(f"⚠️ Could not extract audio info: {stderr.decode()}")
                return {}
        
        except FileNotFoundError:
            logger.warning("⚠️ FFprobe not installed. Cannot extract detailed audio info.")
            return {}
        except Exception as e:
            logger.error(f"❌ Error extracting audio info: {e}")
            return {}
    
    @staticmethod
    def get_audio_duration(file_path: str) -> Optional[float]:
        """Get audio file duration in seconds"""
        try:
            import subprocess
            
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:noprint_sections=1",
                file_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                logger.info(f"✅ Audio duration: {duration}s")
                return duration
            else:
                logger.warning(f"⚠️ Could not get duration: {result.stderr}")
                return None
        
        except (FileNotFoundError, ValueError, subprocess.SubprocessError) as e:
            logger.warning(f"⚠️ Error getting duration: {e}")
            return None
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration from seconds to MM:SS format"""
        try:
            if seconds < 0:
                return "0:00"
            
            mins = int(seconds) // 60
            secs = int(seconds) % 60
            
            return f"{mins}:{secs:02d}"
        except Exception as e:
            logger.error(f"❌ Error formatting duration: {e}")
            return "0:00"
    
    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Remove temporary audio file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Removed temporary file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error removing file: {e}")
            return False
    
    @staticmethod
    async def cleanup_old_files(directory: str, max_age_seconds: int = 3600) -> int:
        """Remove old temporary files from directory"""
        try:
            import time
            
            if not os.path.exists(directory):
                return 0
            
            current_time = time.time()
            removed_count = 0
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        try:
                            os.remove(file_path)
                            removed_count += 1
                            logger.info(f"🗑️ Removed old file: {file_path}")
                        except Exception as e:
                            logger.error(f"❌ Error removing old file: {e}")
            
            logger.info(f"✅ Cleanup complete: {removed_count} files removed")
            return removed_count
        
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0


# ========================
# Utility Functions
# ========================

async def process_audio_file(file_path: str) -> Dict[str, Any]:
    """Main function to process audio file"""
    processor = AudioProcessor()
    
    result = {
        "success": False,
        "file_path": file_path,
        "format": None,
        "size": None,
        "duration": None,
        "info": {},
        "error": None,
    }
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            result["error"] = "File does not exist"
            logger.error(result["error"])
            return result
        
        # Get file format
        file_format = processor.get_file_format(file_path)
        result["format"] = file_format
        
        # Check if format is supported
        if not processor.is_valid_format(file_path):
            result["error"] = f"Unsupported format: {file_format}"
            logger.error(result["error"])
            return result
        
        # Get file size
        file_size = processor.get_file_size(file_path)
        result["size"] = file_size
        
        # Get audio duration
        duration = processor.get_audio_duration(file_path)
        result["duration"] = duration
        
        # Extract audio info
        audio_info = await processor.extract_audio_info(file_path)
        result["info"] = audio_info
        
        result["success"] = True
        logger.info(f"✅ Audio file processed successfully: {file_path}")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Error processing audio file: {e}")
    
    return result


if __name__ == "__main__":
    # Test audio processor
    print("🎵 Audio Processor Test")
    print("=" * 50)
    
    processor = AudioProcessor()
    print(f"Supported formats: {processor.supported_formats}")
    print("=" * 50)
