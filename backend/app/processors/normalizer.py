import ffmpeg
import subprocess
from PIL import Image
from typing import Optional
import tempfile
import os


class MediaNormalizer:
    """Normalize media files to standard formats"""
    
    @staticmethod
    def normalize_video(input_path: str, output_path: str) -> bool:
        """
        Transcode video to H.264/AAC for consistency
        
        Args:
            input_path: Path to input video file
            output_path: Path to output normalized video file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use FFmpeg to transcode to H.264/AAC
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    preset='medium',
                    crf=23,
                    movflags='faststart'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode('utf8')}")
            return False
        except Exception as e:
            print(f"Video normalization error: {e}")
            return False
    
    @staticmethod
    def normalize_image(input_path: str, output_path: str) -> bool:
        """
        Convert image to sRGB color space and standard format
        
        Args:
            input_path: Path to input image file
            output_path: Path to output normalized image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            image = Image.open(input_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to sRGB color profile
            if image.info.get('color_space') != 'sRGB':
                # Simple conversion - in production, use proper ICC profile conversion
                image = image.convert('RGB')
            
            # Save as JPEG for consistency
            image.save(output_path, 'JPEG', quality=85, optimize=True)
            return True
            
        except Exception as e:
            print(f"Image normalization error: {e}")
            return False
    
    @staticmethod
    def generate_thumbnail(input_path: str, output_path: str, size: tuple = (300, 300)) -> bool:
        """
        Generate thumbnail from image or video
        
        Args:
            input_path: Path to input file
            output_path: Path to output thumbnail
            size: Thumbnail size (width, height)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_ext = os.path.splitext(input_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                # Image thumbnail
                image = Image.open(input_path)
                image.thumbnail(size, Image.Resampling.LANCZOS)
                image.save(output_path, 'JPEG', quality=80)
                return True
                
            elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
                # Video thumbnail - extract frame at 1 second
                (
                    ffmpeg
                    .input(input_path, ss='00:00:01')
                    .output(output_path, vframes=1, format='image2', vcodec='mjpeg')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                return True
                
        except Exception as e:
            print(f"Thumbnail generation error: {e}")
            return False
    
    @staticmethod
    def get_video_duration(file_path: str) -> Optional[float]:
        """Get video duration in seconds"""
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None
    
    @staticmethod
    def extract_frame(file_path: str, output_path: str, timestamp: str = '00:00:01') -> bool:
        """
        Extract a single frame from video at specific timestamp
        
        Args:
            file_path: Path to video file
            output_path: Path to save extracted frame
            timestamp: Timestamp in format HH:MM:SS
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            (
                ffmpeg
                .input(file_path, ss=timestamp)
                .output(output_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except Exception as e:
            print(f"Frame extraction error: {e}")
            return False
