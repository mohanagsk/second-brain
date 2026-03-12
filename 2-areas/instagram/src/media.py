"""
media.py - FFmpeg wrapper for audio and frame extraction
"""
import subprocess
import os
from pathlib import Path
from typing import List, Optional


class MediaProcessor:
    """Handle video processing with ffmpeg"""
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_audio(self, video_path: str, output_name: Optional[str] = None) -> str:
        """
        Extract audio from video as MP3
        
        Args:
            video_path: Path to input video
            output_name: Optional custom output filename
            
        Returns:
            Path to extracted audio file
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        if output_name is None:
            output_name = video_path.stem + "_audio.mp3"
        
        output_path = self.output_dir / output_name
        
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-ab", "192k",  # 192kbps audio
            "-ar", "44100",  # 44.1kHz sample rate
            "-y",  # Overwrite
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return str(output_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr}")
    
    def extract_frames(self, video_path: str, num_frames: int = 5, 
                      output_prefix: Optional[str] = None) -> List[str]:
        """
        Extract evenly-spaced frames from video
        
        Args:
            video_path: Path to input video
            num_frames: Number of frames to extract
            output_prefix: Optional custom prefix for output files
            
        Returns:
            List of paths to extracted frame images
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        if output_prefix is None:
            output_prefix = video_path.stem
        
        # Get video duration
        duration_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(duration_cmd, check=True, capture_output=True, text=True)
            duration = float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError) as e:
            raise RuntimeError(f"Failed to get video duration: {e}")
        
        # Calculate frame timestamps
        interval = duration / (num_frames + 1)
        timestamps = [interval * (i + 1) for i in range(num_frames)]
        
        frame_paths = []
        for i, ts in enumerate(timestamps):
            output_path = self.output_dir / f"{output_prefix}_frame_{i+1:02d}.jpg"
            
            cmd = [
                "ffmpeg", "-ss", str(ts),
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2",  # High quality
                "-y",
                str(output_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                frame_paths.append(str(output_path))
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to extract frame {i+1}: {e.stderr}")
                continue
        
        return frame_paths
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata (duration, resolution, codec)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name,duration",
            "-show_entries", "format=duration",
            "-of", "json",
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            import json
            data = json.loads(result.stdout)
            
            stream = data.get("streams", [{}])[0]
            format_data = data.get("format", {})
            
            return {
                "width": stream.get("width"),
                "height": stream.get("height"),
                "codec": stream.get("codec_name"),
                "duration": float(format_data.get("duration", 0))
            }
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to get video info: {e}")


if __name__ == "__main__":
    # Test the processor
    processor = MediaProcessor()
    print("MediaProcessor initialized successfully")
