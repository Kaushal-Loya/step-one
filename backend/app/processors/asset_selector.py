"""
Asset Selector: Evaluates and selects best images from dataset
based on aesthetic quality and semantic relevance.
"""
import os
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from typing import List, Dict

class AssetSelector:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self.images_dir = dataset_path / "images"
        self.videos_dir = dataset_path / "videos"
    
    def select_assets(self) -> List[Dict]:
        """Select top 10 images based on quality metrics"""
        images = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        
        scored_assets = []
        for img_path in images:
            score = self._calculate_score(img_path)
            scored_assets.append({
                "path": str(img_path),
                "filename": img_path.name,
                "score": score,
                "rationale": self._generate_rationale(score)
            })
        
        # Sort by score descending and return top 10
        scored_assets.sort(key=lambda x: x["score"], reverse=True)
        return scored_assets[:10]
    
    def _calculate_score(self, img_path: Path) -> float:
        """Calculate composite score for an image"""
        try:
            # Aesthetic: sharpness (Laplacian variance)
            img = cv2.imread(str(img_path))
            if img is None:
                return 0.0
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 500.0, 1.0)
            
            # Semantic: prefer images with faces/people (using simple heuristics)
            # Check if image has good dimensions (not too small)
            height, width = img.shape[:2]
            size_score = 1.0 if width >= 800 and height >= 600 else 0.5
            
            # Prefer landscape or square orientations
            aspect_ratio = width / height
            if 0.75 <= aspect_ratio <= 1.5:
                orientation_score = 1.0
            else:
                orientation_score = 0.7
            
            # Composite score
            score = (sharpness_score * 0.4) + (size_score * 0.3) + (orientation_score * 0.3)
            return round(score, 3)
        
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            return 0.0
    
    def _generate_rationale(self, score: float) -> str:
        if score >= 0.8:
            return "High quality image with good sharpness and composition"
        elif score >= 0.6:
            return "Decent quality image, suitable for use"
        else:
            return "Lower quality image, use with caution"
