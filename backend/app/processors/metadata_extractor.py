from PIL import Image
from PIL.ExifTags import TAGS
import subprocess
import json
from typing import Dict, Optional, Tuple
from app.models.asset import Orientation, EXIFMetadata, VideoMetadata
import tempfile
import os


class MetadataExtractor:
    """Extract metadata from images and videos"""
    
    @staticmethod
    def extract_image_metadata(file_path: str) -> Dict:
        """Extract EXIF metadata from image file"""
        try:
            image = Image.open(file_path)
            
            # Get dimensions
            width, height = image.size
            
            # Determine orientation
            if width > height:
                orientation = Orientation.LANDSCAPE
            elif height > width:
                orientation = Orientation.PORTRAIT
            else:
                orientation = Orientation.SQUARE
            
            # Extract EXIF data
            exif_data = {}
            if hasattr(image, '_getexif'):
                exif_info = image._getexif()
                if exif_info:
                    for tag, value in exif_info.items():
                        decoded = TAGS.get(tag, tag)
                        exif_data[decoded] = value
            
            # Create structured EXIF metadata
            exif_metadata = EXIFMetadata(
                camera=exif_data.get('Make') or exif_data.get('Model'),
                lens=exif_data.get('LensModel'),
                iso=exif_data.get('ISOSpeedRatings'),
                aperture=exif_data.get('FNumber'),
                shutter_speed=exif_data.get('ExposureTime'),
                focal_length=exif_data.get('FocalLength'),
                color_space=exif_data.get('ColorSpace')
            )
            
            return {
                "dimensions": {"width": width, "height": height},
                "orientation": orientation,
                "exif": exif_metadata.model_dump(exclude_none=True),
                "format": image.format,
                "mode": image.mode
            }
            
        except Exception as e:
            print(f"Error extracting image metadata: {e}")
            return {
                "dimensions": {"width": 0, "height": 0},
                "orientation": Orientation.LANDSCAPE,
                "exif": {},
                "format": "unknown",
                "mode": "unknown"
            }
    
    @staticmethod
    def extract_video_metadata(file_path: str) -> Dict:
        """Extract metadata from video file using FFprobe"""
        try:
            # Use FFprobe to get video metadata
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFprobe error: {result.stderr}")
                return {}
            
            metadata = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            audio_stream = None
            
            for stream in metadata.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            if not video_stream:
                return {}
            
            # Get dimensions
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            # Determine orientation
            if width > height:
                orientation = Orientation.LANDSCAPE
            elif height > width:
                orientation = Orientation.PORTRAIT
            else:
                orientation = Orientation.SQUARE
            
            # Get duration
            duration = float(metadata.get('format', {}).get('duration', 0))
            
            # Create video metadata
            video_metadata = VideoMetadata(
                codec=video_stream.get('codec_name'),
                bitrate=int(metadata.get('format', {}).get('bit_rate', 0)),
                frame_rate=eval(video_stream.get('r_frame_rate', '0/1')),
                audio_channels=len([s for s in metadata.get('streams', []) if s.get('codec_type') == 'audio'])
            )
            
            return {
                "dimensions": {"width": width, "height": height},
                "orientation": orientation,
                "duration_seconds": duration,
                "video": video_metadata.model_dump(exclude_none=True),
                "format": metadata.get('format', {}).get('format_name', 'unknown')
            }
            
        except Exception as e:
            print(f"Error extracting video metadata: {e}")
            return {
                "dimensions": {"width": 0, "height": 0},
                "orientation": Orientation.LANDSCAPE,
                "duration_seconds": 0,
                "video": {},
                "format": "unknown"
            }
    
    @staticmethod
    def extract_from_s3(s3_key: str, s3_service, download_path: str) -> Dict:
        """Download file from S3 and extract metadata"""
        try:
            # Download file
            s3_service.s3_client.download_file(
                s3_service.bucket,
                s3_key,
                download_path
            )
            
            # Determine file type and extract metadata
            file_ext = os.path.splitext(download_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']:
                return MetadataExtractor.extract_image_metadata(download_path)
            elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
                return MetadataExtractor.extract_video_metadata(download_path)
            else:
                return {}
                
        except Exception as e:
            print(f"Error extracting metadata from S3: {e}")
            return {}
