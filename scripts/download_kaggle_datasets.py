"""
Download 2 event datasets (50-150 mixed images/videos each) from Kaggle.
Requires Kaggle API credentials: https://www.kaggle.com/settings
"""

import os
import subprocess
from pathlib import Path
import shutil
import json

def check_kaggle_installed():
    try:
        result = subprocess.run(["kaggle", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_kaggle():
    print("Installing Kaggle CLI...")
    subprocess.run(["pip", "install", "kaggle"], check=True)
    print("✓ Kaggle CLI installed")

def setup_kaggle_credentials():
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        print("✓ Kaggle credentials found")
        return True
    
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    
    if username and key:
        with open(kaggle_json, "w") as f:
            json.dump({"username": username, "key": key}, f)
        kaggle_json.chmod(0o600)
        print("✓ Kaggle credentials set from environment variables")
        return True
    
    print("=" * 60)
    print("KAGGLE API CREDENTIALS REQUIRED")
    print("=" * 60)
    print("1. Go to: https://www.kaggle.com/settings")
    print("2. Click 'Create New API Token' and download kaggle.json")
    print(f"3. Place it in: {kaggle_dir}")
    print("\nOR set environment variables:")
    print("  export KAGGLE_USERNAME='your_username'")
    print("  export KAGGLE_KEY='your_api_key'")
    print("=" * 60)
    return False

def download_kaggle_dataset(dataset_slug: str, output_dir: Path, dataset_name: str):
    try:
        print(f"Downloading {dataset_name} ({dataset_slug})...")
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset_slug, "-p", str(output_dir), "--unzip"],
            capture_output=True, text=True, check=True
        )
        print(f"✓ Downloaded {dataset_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download {dataset_name}: {e.stderr}")
        return False

def organize_dataset(dataset_dir: Path, dataset_label: str):
    images_dir = dataset_dir / "images"
    videos_dir = dataset_dir / "videos"
    images_dir.mkdir(exist_ok=True)
    videos_dir.mkdir(exist_ok=True)
    
    image_exts = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
    video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    
    for file in dataset_dir.rglob("*"):
        if file.is_file():
            ext = file.suffix.lower()
            if ext in image_exts and file.parent != images_dir:
                shutil.move(str(file), str(images_dir / file.name))
            elif ext in video_exts and file.parent != videos_dir:
                shutil.move(str(file), str(videos_dir / file.name))
    
    img_count = len(list(images_dir.glob("*")))
    vid_count = len(list(videos_dir.glob("*")))
    print(f"✓ {dataset_label}: {img_count} images, {vid_count} videos")
    
    if img_count + vid_count < 50:
        print(f"⚠ Warning: {dataset_label} has fewer than 50 total assets.")
    if img_count + vid_count > 150:
        print(f"⚠ Warning: {dataset_label} has more than 150 total assets.")

def create_event_datasets():
    output_dir = Path("/Users/priyanshnarang/Desktop/stepone-ai/event_datasets")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("DOWNLOADING 2 EVENT DATASETS FROM KAGGLE")
    print("=" * 60)
    
    if not check_kaggle_installed():
        install_kaggle()
    
    if not setup_kaggle_credentials():
        print("\nCannot proceed without Kaggle credentials.")
        return False
    
    # Dataset 1: Conference Event
    dataset1_dir = output_dir / "event_dataset_1_conference"
    dataset1_dir.mkdir(exist_ok=True)
    
    print("\n[1/2] Downloading Conference Event Dataset...")
    download_kaggle_dataset(
        dataset_slug="iamsouravbanerjee/event-photography-dataset",
        output_dir=dataset1_dir,
        dataset_name="Conference Images"
    )
    download_kaggle_dataset(
        dataset_slug="prateekgarg/event-video-dataset",
        output_dir=dataset1_dir,
        dataset_name="Conference Videos"
    )
    organize_dataset(dataset1_dir, "Dataset 1 (Conference)")
    
    # Dataset 2: Workshop/Meeting Event
    dataset2_dir = output_dir / "event_dataset_2_meeting"
    dataset2_dir.mkdir(exist_ok=True)
    
    print("\n[2/2] Downloading Workshop/Meeting Event Dataset...")
    download_kaggle_dataset(
        dataset_slug="shubhamsingh0209/event-image-dataset",
        output_dir=dataset2_dir,
        dataset_name="Workshop Images"
    )
    download_kaggle_dataset(
        dataset_slug="jainaric8/event-videos",
        output_dir=dataset2_dir,
        dataset_name="Workshop Videos"
    )
    organize_dataset(dataset2_dir, "Dataset 2 (Workshop)")
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print(f"\nDatasets saved to: {output_dir.absolute()}")
    print("\nVerify each dataset has 50-150 mixed images/videos before proceeding.")
    return True

if __name__ == "__main__":
    create_event_datasets()
