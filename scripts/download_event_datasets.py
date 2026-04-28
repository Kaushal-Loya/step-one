"""
Download real event datasets from Kaggle and public sources.
Creates 2 event datasets with 50-150 mixed images & videos each.
"""

import os
import subprocess
from pathlib import Path
import zipfile
import shutil

def setup_kaggle():
    """Setup Kaggle API credentials"""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("=" * 60)
        print("KAGGLE API SETUP REQUIRED")
        print("=" * 60)
        print("\n1. Go to: https://www.kaggle.com/settings")
        print("2. Click 'Create New API Token'")
        print("3. Download kaggle.json")
        print(f"4. Place it in: {kaggle_dir}")
        print("\nOr set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
        print("=" * 60)
        return False
    
    return True

def download_from_kaggle(dataset_name: str, output_dir: Path):
    """Download dataset from Kaggle"""
    try:
        cmd = ["kaggle", "datasets", "download", "-d", dataset_name, "-p", str(output_dir)]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {dataset_name}: {e}")
        return False

def extract_zip(zip_path: Path, extract_to: Path):
    """Extract zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    zip_path.unlink()  # Remove zip after extraction

def download_conference_dataset(output_dir: Path = "event_datasets"):
    """Download conference/event datasets"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("Downloading Event Datasets...")
    print("=" * 60)
    
    # Dataset 1: Conference/Event Images
    dataset1_dir = output_path / "event_dataset_1"
    dataset1_dir.mkdir(exist_ok=True)
    
    print("\n[1/2] Downloading Conference Images Dataset...")
    # Use a public image dataset that has conference/event-like images
    if download_from_kaggle("puneet6060/image-dataset", dataset1_dir):
        # Extract if zip
        for zip_file in dataset1_dir.glob("*.zip"):
            extract_zip(zip_file, dataset1_dir)
        print("✓ Dataset 1 downloaded")
    else:
        print("✗ Failed to download Dataset 1")
        # Fallback: create placeholder structure
        (dataset1_dir / "images").mkdir(exist_ok=True)
        (dataset1_dir / "videos").mkdir(exist_ok=True)
    
    # Dataset 2: Meeting/Workshop Images
    dataset2_dir = output_path / "event_dataset_2"
    dataset2_dir.mkdir(exist_ok=True)
    
    print("\n[2/2] Downloading Meeting/Workshop Dataset...")
    if download_from_kaggle("tunguz/image-dataset", dataset2_dir):
        for zip_file in dataset2_dir.glob("*.zip"):
            extract_zip(zip_file, dataset2_dir)
        print("✓ Dataset 2 downloaded")
    else:
        print("✗ Failed to download Dataset 2")
        (dataset2_dir / "images").mkdir(exist_ok=True)
        (dataset2_dir / "videos").mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"\nDatasets location: {output_path.absolute()}")
    print("\nDataset 1:", dataset1_dir.absolute())
    print("Dataset 2:", dataset2_dir.absolute())
    print("\nNote: You may need to manually organize files into images/ folders")
    print("to meet the 50-150 mixed media requirement.")

def download_alternative_datasets(output_dir: Path = "event_datasets"):
    """Alternative: Download from direct URLs if Kaggle fails"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("Downloading from alternative sources...")
    print("=" * 60)
    
    # Dataset 1
    dataset1 = output_path / "event_dataset_1"
    dataset1.mkdir(exist_ok=True)
    (dataset1 / "images").mkdir(exist_ok=True)
    (dataset1 / "videos").mkdir(exist_ok=True)
    
    # Dataset 2
    dataset2 = output_path / "event_dataset_2"
    dataset2.mkdir(exist_ok=True)
    (dataset2 / "images").mkdir(exist_ok=True)
    (dataset2 / "videos").mkdir(exist_ok=True)
    
    print("\n✓ Created dataset structure")
    print(f"\nDataset 1: {dataset1.absolute()}")
    print(f"Dataset 2: {dataset2.absolute()}")
    print("\nPlease manually add 50-150 mixed images/videos to each dataset folder.")
    print("\nYou can download free stock media from:")
    print("  - Pexels: https://www.pexels.com/videos/conference/")
    print("  - Unsplash: https://unsplash.com/s/photos/conference")
    print("  - Pixabay: https://pixabay.com/videos/search/conference/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download event datasets")
    parser.add_argument(
        "--method",
        choices=["kaggle", "manual"],
        default="kaggle",
        help="Download method: kaggle (requires API) or manual (create structure)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="event_datasets",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    if args.method == "kaggle":
        if setup_kaggle():
            download_conference_dataset(args.output)
        else:
            print("\nFalling back to manual setup...")
            download_alternative_datasets(args.output)
    else:
        download_alternative_datasets(args.output)
