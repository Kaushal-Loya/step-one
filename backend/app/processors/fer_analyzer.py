from fer import FER
import cv2
from typing import List, Dict, Optional
import numpy as np
from app.models.asset import DetectedFace, EmotionScores


class FERAnalyzer:
    """Facial Expression Recognition using FER library"""
    
    def __init__(self):
        """Initialize FER detector"""
        try:
            # Initialize FER detector
            # mtcnn=True for better face detection, but slower
            # mtcnn=False for faster detection with OpenCV
            self.detector = FER(mtcnn=False)
            print("FER detector initialized successfully")
        except Exception as e:
            print(f"Error initializing FER detector: {e}")
            self.detector = None
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze facial expressions in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing detected faces and emotion scores
        """
        if not self.detector:
            return {"faces": [], "emotions": EmotionScores().model_dump()}
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {"faces": [], "emotions": EmotionScores().model_dump()}
            
            # Detect emotions
            results = self.detector.detect_emotions(image)
            
            detected_faces = []
            emotion_totals = {
                "angry": 0.0,
                "disgust": 0.0,
                "fear": 0.0,
                "happy": 0.0,
                "sad": 0.0,
                "surprise": 0.0,
                "neutral": 0.0
            }
            
            for result in results:
                # Get bounding box
                box = result["box"]
                x, y, w, h = box
                bbox = [float(x), float(y), float(x + w), float(y + h)]
                
                # Get emotions
                emotions = result["emotions"]
                
                # Find dominant emotion
                dominant_emotion = max(emotions, key=emotions.get)
                confidence = emotions[dominant_emotion]
                
                # Create DetectedFace
                detected_faces.append(
                    DetectedFace(
                        bbox=bbox,
                        emotion=dominant_emotion,
                        confidence=float(confidence)
                    )
                )
                
                # Accumulate emotion scores
                for emotion, score in emotions.items():
                    emotion_totals[emotion] += score
            
            # Calculate average emotions across all faces
            face_count = len(detected_faces)
            if face_count > 0:
                avg_emotions = {
                    emotion: round(score / face_count, 3)
                    for emotion, score in emotion_totals.items()
                }
            else:
                avg_emotions = emotion_totals
            
            return {
                "faces": detected_faces,
                "emotions": EmotionScores(**avg_emotions).model_dump(),
                "face_count": face_count
            }
            
        except Exception as e:
            print(f"Error analyzing facial expressions: {e}")
            return {"faces": [], "emotions": EmotionScores().model_dump(), "face_count": 0}
    
    def get_room_energy_score(self, image_path: str) -> float:
        """
        Calculate room energy score based on detected emotions
        Higher score = more engaged/happy crowd
        
        Args:
            image_path: Path to image file
            
        Returns:
            float: Room energy score (0-1)
        """
        result = self.analyze_image(image_path)
        emotions = result.get("emotions", {})
        face_count = result.get("face_count", 0)
        
        if face_count == 0:
            return 0.0
        
        # Weight positive emotions higher
        energy_score = (
            emotions.get("happy", 0.0) * 1.0 +
            emotions.get("surprise", 0.0) * 0.7 +
            emotions.get("neutral", 0.0) * 0.5 +
            emotions.get("sad", 0.0) * 0.2 +
            emotions.get("angry", 0.0) * 0.1 +
            emotions.get("fear", 0.0) * 0.1 +
            emotions.get("disgust", 0.0) * 0.1
        )
        
        # Normalize by face count (more faces = higher potential energy)
        # But cap at 1.0
        normalized_score = min(energy_score * (1 + face_count * 0.1), 1.0)
        
        return round(normalized_score, 3)
    
    def count_faces(self, image_path: str) -> int:
        """Count number of faces in an image"""
        result = self.analyze_image(image_path)
        return result.get("face_count", 0)
    
    def get_dominant_emotion(self, image_path: str) -> Optional[str]:
        """
        Get the dominant emotion across all faces in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Dominant emotion or None
        """
        result = self.analyze_image(image_path)
        emotions = result.get("emotions", {})
        
        if not emotions:
            return None
        
        return max(emotions, key=emotions.get)
    
    def is_engaged_crowd(self, image_path: str, threshold: float = 0.6) -> bool:
        """
        Determine if the crowd appears engaged based on emotion analysis
        
        Args:
            image_path: Path to image file
            threshold: Minimum energy score for engaged crowd
            
        Returns:
            bool: True if crowd is engaged
        """
        energy_score = self.get_room_energy_score(image_path)
        return energy_score >= threshold


# Singleton instance
fer_analyzer = FERAnalyzer()
