"""
Download real event/conference images and videos from free stock media sites.
Creates 2 event datasets with 50-150 mixed files each.
No API keys required - uses direct downloads from Pexels/Unsplash.
"""

import os
import requests
from pathlib import Path
import time
from typing import List

# Real conference/event images from Unsplash (free, no API needed)
CONFERENCE_IMAGES = [
    "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800",
    "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=800",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800",
    "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800",
    "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800",
    "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800",
    "https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=800",
    "https://images.unsplash.com/photo-1559223607-a43c990c692c?w=800",
    "https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=800",
    "https://images.unsplash.com/photo-1560439514-4e9645039924?w=800",
    "https://images.unsplash.com/photo-1504384764586-bb4cdc1707b0?w=800",
    "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800",
    "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=800",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800",
    "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
    "https://images.unsplash.com/photo-1573164713988-8665fc963095?w=800",
    "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800",
    "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=800",
    "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800",
]

# Real meeting/workshop images
MEETING_IMAGES = [
    "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800",
    "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800",
    "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800",
    "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800",
    "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=800",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800",
    "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800",
]

# Real conference videos from Pexels (free, no API needed)
CONFERENCE_VIDEOS = [
    "https://videos.pexels.com/video-files/3129671/3129671-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/5492777/5492777-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/854292/854292-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/3129593/3129593-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/853877/853877-uhd_2560_1440_25fps.mp4",
]

MEETING_VIDEOS = [
    "https://videos.pexels.com/video-files/3195394/3195394-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/5439399/5439399-uhd_2560_1440_25fps.mp4",
    "https://videos.pexels.com/video-files/6999556/6999556-uhd_2560_1440_25fps.mp4",
]

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from URL to destination path"""
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ {dest_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {dest_path.name} - {e}")
        return False

def create_dataset(
    dataset_name: str,
    image_urls: List[str],
    video_urls: List[str],
    output_dir: Path,
    target_count: int = 60
):
    """Create a single event dataset"""
    dataset_path = output_dir / dataset_name
    images_dir = dataset_path / "images"
    videos_dir = dataset_path / "videos"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreating {dataset_name}...")
    print(f"Target: {target_count} files")
    print("-" * 50)
    
    # Calculate distribution (70% images, 30% videos)
    image_count = int(target_count * 0.7)
    video_count = target_count - image_count
    
    downloaded_images = 0
    downloaded_videos = 0
    
    # Download images (cycle through URLs to reach target)
    print("Downloading images...")
    while downloaded_images < image_count:
        for img_url in image_urls:
            if downloaded_images >= image_count:
                break
            
            filename = f"img_{downloaded_images + 1:03d}.jpg"
            dest_path = images_dir / filename
            
            if download_file(img_url, dest_path):
                downloaded_images += 1
                time.sleep(0.3)
    
    # Download videos
    print("Downloading videos...")
    while downloaded_videos < video_count:
        for vid_url in video_urls:
            if downloaded_videos >= video_count:
                break
            
            filename = f"vid_{downloaded_videos + 1:03d}.mp4"
            dest_path = videos_dir / filename
            
            if download_file(vid_url, dest_path):
                downloaded_videos += 1
                time.sleep(0.5)
    
    print("-" * 50)
    print(f"✓ {dataset_name}: {downloaded_images} images, {downloaded_videos} videos")
    
    return downloaded_images + downloaded_videos

def main():
    output_dir = Path("event_datasets")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("DOWNLOADING 2 EVENT DATASETS")
    print("=" * 60)
    print("\nSource: Pexels & Unsplash (free, no API required)")
    print("License: Free to use for commercial purposes")
    print("=" * 60)
    
    # Dataset 1: Conference
    total1 = create_dataset(
        "event_dataset_1_conference",
        CONFERENCE_IMAGES,
        CONFERENCE_VIDEOS,
        output_dir,
        target_count=60
    )
    
    # Dataset 2: Meeting/Workshop
    total2 = create_dataset(
        "event_dataset_2_meeting",
        MEETING_IMAGES,
        MEETING_VIDEOS,
        output_dir,
        target_count=60
    )
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"\nTotal files downloaded: {total1 + total2}")
    print(f"\nLocation: {output_dir.absolute()}")
    print("\nDataset 1 (Conference):")
    print(f"  {output_dir / 'event_dataset_1_conference'}")
    print("\nDataset 2 (Meeting):")
    print(f"  {output_dir / 'event_dataset_2_meeting'}")
    print("\nEach dataset has mixed images and videos ready for upload!")
    print("Upload each dataset via the frontend at http://localhost:5173")

if __name__ == "__main__":
    main()
