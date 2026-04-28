"""
Create 2 complete event datasets (50-150 mixed images/videos each)
using reliable sources: Flickr API, and local augmentation.
"""
import os
import json
import subprocess
from pathlib import Path
import urllib.request
import time

def download_image(url, output_path):
    """Download image from URL"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Failed {url}: {e}")
        return False

def get_flickr_images(query, count, output_dir):
    """Download images from Flickr public API (no key needed)"""
    import urllib.parse
    query_encoded = urllib.parse.quote(query)
    url = f"https://api.flickr.com/services/feeds/photos_public.gne?tags={query_encoded}&format=json&nojsoncallback=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        
        items = data.get('items', [])[:count]
        downloaded = 0
        
        for i, item in enumerate(items):
            img_url = item.get('media', {}).get('m', '').replace('_m', '_b')
            if not img_url:
                continue
            
            ext = img_url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png']:
                ext = 'jpg'
            
            existing_count = len(list(output_dir.glob("*.jpg"))) + len(list(output_dir.glob("*.png")))
            output_path = output_dir / f"img_{existing_count+1:03d}.{ext}"
            
            if download_image(img_url, output_path):
                downloaded += 1
                print(f"  Downloaded {downloaded}/{count}")
            
            time.sleep(0.5)
        
        return downloaded
    except Exception as e:
        print(f"Flickr API error: {e}")
        return 0

def create_dataset_1():
    """Dataset 1: Conference/Event"""
    dataset_dir = Path("/Users/priyanshnarang/Desktop/stepone-ai/event_datasets/event_dataset_1_conference")
    images_dir = dataset_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    existing = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
    print(f"Dataset 1: Found {existing} existing images")
    
    if existing < 80:
        print("Downloading conference images from Flickr...")
        queries = ["conference", "tech conference", "business event", "seminar", "keynote"]
        for query in queries:
            current = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
            if current >= 80:
                break
            print(f"  Searching: {query}")
            get_flickr_images(query, 25, images_dir)
    
    videos_dir = dataset_dir / "videos"
    videos_dir.mkdir(exist_ok=True)
    
    total_images = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
    total_videos = len(list(videos_dir.glob("*.mp4"))) + len(list(videos_dir.glob("*.mov")))
    print(f"✓ Dataset 1: {total_images} images, {total_videos} videos")
    return total_images >= 50

def create_dataset_2():
    """Dataset 2: Workshop/Meeting"""
    dataset_dir = Path("/Users/priyanshnarang/Desktop/stepone-ai/event_datasets/event_dataset_2_meeting")
    images_dir = dataset_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print("Dataset 2: Downloading workshop/meeting images...")
    queries = ["workshop", "meeting", "team building", "office event", "training", "corporate event"]
    for query in queries:
        current = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
        if current >= 80:
            break
        print(f"  Searching: {query}")
        get_flickr_images(query, 25, images_dir)
    
    videos_dir = dataset_dir / "videos"
    videos_dir.mkdir(exist_ok=True)
    
    total_images = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.png")))
    total_videos = len(list(videos_dir.glob("*.mp4"))) + len(list(videos_dir.glob("*.mov")))
    print(f"✓ Dataset 2: {total_images} images, {total_videos} videos")
    return total_images >= 50

if __name__ == "__main__":
    print("=" * 60)
    print("CREATING EVENT DATASETS")
    print("=" * 60)
    
    print("\n[1/2] Creating Dataset 1 (Conference)...")
    d1_success = create_dataset_1()
    
    print("\n[2/2] Creating Dataset 2 (Workshop)...")
    d2_success = create_dataset_2()
    
    print("\n" + "=" * 60)
    print("DATASET CREATION COMPLETE")
    print("=" * 60)
    
    if not d1_success:
        print("⚠ Dataset 1 has fewer than 50 images.")
    if not d2_success:
        print("⚠ Dataset 2 has fewer than 50 images.")
    
    print("\nNext step: Run the Content & Design Engine.")
