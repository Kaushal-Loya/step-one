import ffmpeg
from typing import List, Dict, Optional
import tempfile
import os


class ReelGenerator:
    """Generate Instagram Reels from selected video clips"""
    
    def __init__(self):
        """Initialize reel generator"""
        self.target_resolution = (1080, 1920)  # 9:16 vertical
        self.target_fps = 30
        self.target_bitrate = "5M"
    
    def create_reel(
        self,
        video_paths: List[str],
        output_path: Optional[str] = None,
        duration: float = 30.0,
        transition: str = "fade"
    ) -> Optional[str]:
        """
        Create Instagram reel from video clips
        
        Args:
            video_paths: List of video file paths
            output_path: Path to save reel
            duration: Target duration in seconds
            transition: Transition type ("fade", "cut", "dissolve")
            
        Returns:
            str: Path to generated reel or None
        """
        try:
            if not video_paths:
                return None
            
            # Calculate duration per clip
            clip_duration = duration / len(video_paths)
            
            # Create filter complex for concatenation with transitions
            filter_complex = self._build_filter_complex(video_paths, clip_duration, transition)
            
            # Build FFmpeg command
            inputs = []
            for path in video_paths:
                inputs.extend(['-i', path])
            
            output_path = output_path or tempfile.mktemp(suffix='.mp4')
            
            (
                ffmpeg
                .input(*inputs)
                .output(
                    output_path,
                    vf=filter_complex,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p',
                    r=self.target_fps,
                    b_v=self.target_bitrate,
                    movflags='+faststart',
                    t=duration
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error creating reel: {e}")
            return None
    
    def _build_filter_complex(
        self,
        video_paths: List[str],
        clip_duration: float,
        transition: str
    ) -> str:
        """Build FFmpeg filter complex for concatenation"""
        num_videos = len(video_paths)
        
        if num_videos == 1:
            # Single video - just resize
            return f"scale={self.target_resolution[0]}:{self.target_resolution[1]},crop={self.target_resolution[0]}:{self.target_resolution[1]}"
        
        # Multiple videos - concatenate with transitions
        filters = []
        
        for i in range(num_videos):
            # Resize and crop each video
            filters.append(f"[{i}:v]scale={self.target_resolution[0]}:{self.target_resolution[1]},crop={self.target_resolution[0]}:{self.target_resolution[1]},setpts=PTS-STARTPTS,ttrim=duration={clip_duration}[v{i}]")
            filters.append(f"[{i}:a]atrim=duration={clip_duration},asetpts=PTS-STARTPTS[a{i}]")
        
        # Concatenate videos
        video_inputs = ",".join([f"[v{i}]" for i in range(num_videos)])
        audio_inputs = ",".join([f"[a{i}]" for i in range(num_videos)])
        
        filters.append(f"{video_inputs}concat=n={num_videos}:v=1:a=0[outv]")
        filters.append(f"{audio_inputs}concat=n={num_videos}:v=0:a=1[outa]")
        
        return ";".join(filters)
    
    def create_reel_from_images(
        self,
        image_paths: List[str],
        output_path: Optional[str] = None,
        duration: float = 30.0,
        effect: str = "kenburns"
    ) -> Optional[str]:
        """
        Create reel from images with Ken Burns effect
        
        Args:
            image_paths: List of image file paths
            output_path: Path to save reel
            duration: Target duration in seconds
            effect: Animation effect ("kenburns", "fade", "zoom")
            
        Returns:
            str: Path to generated reel or None
        """
        try:
            if not image_paths:
                return None
            
            image_duration = duration / len(image_paths)
            
            # Create filter complex for image slideshow
            filter_parts = []
            
            for i, path in enumerate(image_paths):
                # Scale and add zoom effect
                if effect == "kenburns":
                    filter_parts.append(f"[{i}:v]scale={self.target_resolution[0]}:{self.target_resolution[1]},zoompan=z='min(zoom+0.0015,1.5)':d={int(image_duration)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v{i}]")
                elif effect == "zoom":
                    filter_parts.append(f"[{i}:v]scale={self.target_resolution[0]}:{self.target_resolution[1]},zoompan=z='1.2':d={int(image_duration)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v{i}]")
                else:
                    filter_parts.append(f"[{i}:v]scale={self.target_resolution[0]}:{self.target_resolution[1]}[v{i}]")
            
            # Concatenate
            video_inputs = ",".join([f"[v{i}]" for i in range(len(image_paths))])
            filter_parts.append(f"{video_inputs}concat=n={len(image_paths)}[vout]")
            
            filter_complex = ";".join(filter_parts)
            
            # Build inputs
            inputs = []
            for path in image_paths:
                inputs.extend(['-loop', '1', '-i', path])
            
            output_path = output_path or tempfile.mktemp(suffix='.mp4')
            
            (
                ffmpeg
                .input(*inputs)
                .output(
                    output_path,
                    vf=filter_complex,
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    r=self.target_fps,
                    b_v=self.target_bitrate,
                    t=duration
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error creating reel from images: {e}")
            return None
    
    def add_audio_to_reel(
        self,
        reel_path: str,
        audio_path: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Add audio track to reel
        
        Args:
            reel_path: Path to video reel
            audio_path: Path to audio file
            output_path: Path to save video with audio
            
        Returns:
            str: Path to video with audio or None
        """
        try:
            output_path = output_path or tempfile.mktemp(suffix='.mp4')
            
            (
                ffmpeg
                .input(reel_path)
                .input(audio_path)
                .output(
                    output_path,
                    vcodec='copy',
                    acodec='aac',
                    shortest=None
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error adding audio to reel: {e}")
            return None
    
    def add_text_overlay(
        self,
        reel_path: str,
        text: str,
        output_path: Optional[str] = None,
        position: str = "bottom"
    ) -> Optional[str]:
        """
        Add text overlay to reel
        
        Args:
            reel_path: Path to video reel
            text: Text to overlay
            output_path: Path to save video with text
            position: Text position ("top", "bottom", "center")
            
        Returns:
            str: Path to video with text or None
        """
        try:
            output_path = output_path or tempfile.mktemp(suffix='.mp4')
            
            # Calculate text position
            if position == "top":
                text_filter = f"drawtext=text='{text}':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=48:x=(w-tw)/2:y=50:fontcolor=white:shadowx=2:shadowy=2:shadowcolor=black@0.5"
            elif position == "center":
                text_filter = f"drawtext=text='{text}':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=48:x=(w-tw)/2:y=(h-th)/2:fontcolor=white:shadowx=2:shadowy=2:shadowcolor=black@0.5"
            else:  # bottom
                text_filter = f"drawtext=text='{text}':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=48:x=(w-tw)/2:y=h-100:fontcolor=white:shadowx=2:shadowy=2:shadowcolor=black@0.5"
            
            (
                ffmpeg
                .input(reel_path)
                .output(
                    output_path,
                    vf=text_filter,
                    vcodec='libx264',
                    acodec='copy',
                    pix_fmt='yuv420p'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error adding text overlay: {e}")
            return None
    
    
    def extract_highlights(
        self,
        video_path: str,
        timestamps: List[tuple],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract highlight clips from video at specific timestamps
        
        Args:
            video_path: Path to source video
            timestamps: List of (start, end) tuples in seconds
            output_path: Path to save highlights reel
            
        Returns:
            str: Path to highlights reel or None
        """
        try:
            if not timestamps:
                return None
            
            # Create filter complex for concatenating highlights
            filter_parts = []
            
            for i, (start, end) in enumerate(timestamps):
                duration = end - start
                filter_parts.append(f"[0:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS[v{i}]")
                filter_parts.append(f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS[a{i}]")
            
            video_inputs = ",".join([f"[v{i}]" for i in range(len(timestamps))])
            audio_inputs = ",".join([f"[a{i}]" for i in range(len(timestamps))])
            
            filter_parts.append(f"{video_inputs}concat=n={len(timestamps)}:v=1:a=0[outv]")
            filter_parts.append(f"{audio_inputs}concat=n={len(timestamps)}:v=0:a=1[outa]")
            
            filter_complex = ";".join(filter_parts)
            
            output_path = output_path or tempfile.mktemp(suffix='.mp4')
            
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=filter_complex,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error extracting highlights: {e}")
            return None


# Singleton instance
reel_generator = ReelGenerator()
