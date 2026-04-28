import torch
import clip
from PIL import Image
import numpy as np
import cv2
from typing import Dict, Optional
import colorsys


class AestheticScorer:
    """Aesthetic scoring using CLIP for semantic understanding and custom metrics"""
    
    def __init__(self):
        """Initialize CLIP model and device"""
        try:
            # Load CLIP model
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            print(f"CLIP model loaded on {self.device}")
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            self.model = None
            self.preprocess = None
    
    def calculate_composition_score(self, image_path: str) -> float:
        """
        Calculate composition score based on rule of thirds and balance
        
        Args:
            image_path: Path to image file
            
        Returns:
            float: Composition score (0-1)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.5
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Rule of thirds grid
            h, w = gray.shape
            third_h, third_w = h // 3, w // 3
            
            # Calculate edge density in rule of thirds zones
            edges = cv2.Canny(gray, 100, 200)
            
            # Check intersections (rule of thirds points)
            points = [
                (third_w, third_h),
                (2 * third_w, third_h),
                (third_w, 2 * third_h),
                (2 * third_w, 2 * third_h)
            ]
            
            edge_density_at_points = []
            for x, y in points:
                # Sample region around point
                region = edges[max(0, y-10):min(h, y+10), max(0, x-10):min(w, x+10)]
                edge_density_at_points.append(np.sum(region) / region.size)
            
            # Higher edge density at rule of thirds points = better composition
            avg_edge_density = np.mean(edge_density_at_points)
            total_edge_density = np.sum(edges) / edges.size
            
            # Normalize score
            composition_score = min(avg_edge_density / (total_edge_density + 1e-6), 1.0)
            
            return round(composition_score, 3)
            
        except Exception as e:
            print(f"Error calculating composition score: {e}")
            return 0.5
    
    def calculate_lighting_score(self, image_path: str) -> float:
        """
        Calculate lighting score based on brightness distribution
        
        Args:
            image_path: Path to image file
            
        Returns:
            float: Lighting score (0-1)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.5
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # Check for good dynamic range (not too dark, not too bright)
            # Ideal: spread across histogram, not clustered at extremes
            total_pixels = gray.shape[0] * gray.shape[1]
            
            # Count pixels in good range (10-240)
            good_range = np.sum(hist[10:240]) / total_pixels
            
            # Check for blown highlights (>245)
            blown_highlights = np.sum(hist[245:]) / total_pixels
            
            # Check for blocked shadows (<10)
            blocked_shadows = np.sum(hist[:10]) / total_pixels
            
            # Calculate score
            lighting_score = good_range - (blown_highlights + blocked_shadows) * 2
            lighting_score = max(0, min(1, lighting_score))
            
            return round(lighting_score, 3)
            
        except Exception as e:
            print(f"Error calculating lighting score: {e}")
            return 0.5
    
    def calculate_color_harmony_score(self, image_path: str) -> float:
        """
        Calculate color harmony score based on color distribution
        
        Args:
            image_path: Path to image file
            
        Returns:
            float: Color harmony score (0-1)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.5
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Calculate dominant colors using k-means
            pixels = image.reshape(-1, 3)
            pixels = pixels.astype(np.float32)
            
            # Simple color analysis
            # Check for complementary colors (good harmony)
            # Check for color variety
            
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Calculate hue histogram
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            
            # Calculate color spread
            non_zero_bins = np.count_nonzero(hist_h)
            color_variety = min(non_zero_bins / 30, 1.0)  # Normalize to 0-1
            
            # Calculate saturation average
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            avg_saturation = np.average(np.arange(256), weights=hist_s.flatten()) / 256
            
            # Combine metrics
            color_harmony = (color_variety * 0.6 + avg_saturation * 0.4)
            
            return round(color_harmony, 3)
            
        except Exception as e:
            print(f"Error calculating color harmony score: {e}")
            return 0.5
    
    def calculate_clip_score(self, image_path: str, prompt: str = "professional event photography high quality") -> float:
        """
        Calculate CLIP-based semantic score for image quality
        
        Args:
            image_path: Path to image file
            prompt: Text prompt to compare against
            
        Returns:
            float: CLIP similarity score (0-1)
        """
        if not self.model or not self.preprocess:
            return 0.5
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Tokenize text
            text_input = clip.tokenize([prompt]).to(self.device)
            
            # Calculate similarity
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_input)
                
                # Calculate cosine similarity
                similarity = (image_features @ text_features.T).squeeze()
                
                # Normalize to 0-1
                score = (similarity + 1) / 2
                
            return round(float(score), 3)
            
        except Exception as e:
            print(f"Error calculating CLIP score: {e}")
            return 0.5
    
    def calculate_composite_aesthetic_score(
        self,
        image_path: str,
        composition_weight: float = 0.25,
        lighting_weight: float = 0.25,
        color_weight: float = 0.25,
        semantic_weight: float = 0.25
    ) -> float:
        """
        Calculate composite aesthetic score combining all metrics
        
        Args:
            image_path: Path to image file
            composition_weight: Weight for composition score
            lighting_weight: Weight for lighting score
            color_weight: Weight for color harmony score
            semantic_weight: Weight for CLIP semantic score
            
        Returns:
            float: Composite aesthetic score (0-1)
        """
        try:
            composition = self.calculate_composition_score(image_path)
            lighting = self.calculate_lighting_score(image_path)
            color = self.calculate_color_harmony_score(image_path)
            semantic = self.calculate_clip_score(image_path)
            
            # Weighted average
            composite = (
                composition * composition_weight +
                lighting * lighting_weight +
                color * color_weight +
                semantic * semantic_weight
            )
            
            return round(composite, 3)
            
        except Exception as e:
            print(f"Error calculating composite aesthetic score: {e}")
            return 0.5
    
    def get_detailed_scores(self, image_path: str) -> Dict:
        """
        Get all aesthetic scores for an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing all individual and composite scores
        """
        return {
            "composition": self.calculate_composition_score(image_path),
            "lighting": self.calculate_lighting_score(image_path),
            "color_harmony": self.calculate_color_harmony_score(image_path),
            "semantic": self.calculate_clip_score(image_path),
            "composite": self.calculate_composite_aesthetic_score(image_path)
        }


# Singleton instance
aesthetic_scorer = AestheticScorer()
