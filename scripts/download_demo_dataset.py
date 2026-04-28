"""
Download demo dataset for testing the Content & Design Engine.
Downloads 50-150 sample images and videos from free sources.
"""

import os
import requests
from pathlib import Path
from typing import List
import time

# Sample image URLs (Unsplash - free to use)
SAMPLE_IMAGES = [
    "https://images.unsplash.com/photo-1540575467063-178a50c2df87",  # Conference
    "https://images.unsplash.com/photo-1515187029135-18ee286d815b",  # Event
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678",  # Meeting
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2",  # Crowd
    "https://images.unsplash.com/photo-1511578314322-379afb476865",  # Gathering
    "https://images.unsplash.com/photo-1523580494863-6f3031224c94",  # Presentation
    "https://images.unsplash.com/photo-1544531586-fde5298cdd40",  # Workshop
    "https://images.unsplash.com/photo-1559223607-a43c990c692c",  # Stage
    "https://images.unsplash.com/photo-1591115765373-5207764f72e7",  # Networking
    "https://images.unsplash.com/photo-1560439514-4e9645039924",  # People
]

# Sample video URLs (Pexels - free to use)
SAMPLE_VIDEOS = [
    "https://videos.pexels.com/video-files/3129671/3129671-uhd_2560_1440_25fps.mp4",  # Conference
    "https://videos.pexels.com/video-files/5492777/5492777-uhd_2560_1440_25fps.mp4",  # Meeting
    "https://videos.pexels.com/video-files/854292/854292-uhd_2560_1440_25fps.mp4",  # Crowd
]

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from URL to destination path"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded: {dest_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False

def create_demo_dataset(output_dir: str = "demo_dataset", target_count: int = 60):
    """
    Create a demo dataset with mixed images and videos
    
    Args:
        output_dir: Directory to save files
        target_count: Total number of files (50-150)
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"Creating demo dataset with {target_count} files...")
    print(f"Output directory: {output_path.absolute()}")
    
    # Calculate distribution (70% images, 30% videos)
    image_count = int(target_count * 0.7)
    video_count = target_count - image_count
    
    print(f"\nTarget: {image_count} images, {video_count} videos")
    print("-" * 50)
    
    downloaded_images = 0
    downloaded_videos = 0
    
    # Download images
    while downloaded_images < image_count:
        for img_url in SAMPLE_IMAGES:
            if downloaded_images >= image_count:
                break
            
            filename = f"image_{downloaded_images + 1:03d}.jpg"
            dest_path = output_path / "images" / filename
            
            if download_file(img_url, dest_path):
                downloaded_images += 1
                time.sleep(0.5)  # Rate limiting
    
    # Download videos
    while downloaded_videos < video_count:
        for vid_url in SAMPLE_VIDEOS:
            if downloaded_videos >= video_count:
                break
            
            filename = f"video_{downloaded_videos + 1:03d}.mp4"
            dest_path = output_path / "videos" / filename
            
            if download_file(vid_url, dest_path):
                downloaded_videos += 1
                time.sleep(1)  # Rate limiting for videos
    
    print("-" * 50)
    print(f"\n✓ Demo dataset created successfully!")
    print(f"  Images: {downloaded_images}")
    print(f"  Videos: {downloaded_videos}")
    print(f"  Total: {downloaded_images + downloaded_videos}")
    print(f"\nLocation: {output_path.absolute()}")
    print(f"\nYou can now upload these files via the frontend at http://localhost:5173")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download demo dataset for testing")
    parser.add_argument(
        "--count",
        type=int,
        default=60,
        help="Number of files to download (50-150, default: 60)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="demo_dataset",
        help="Output directory (default: demo_dataset)"
    )
    
    args = parser.parse_args()
    
    if args.count < 50 or args.count > 150:
        print("Error: Count must be between 50 and 150")
        exit(1)
    
    create_demo_dataset(args.output, args.count)
