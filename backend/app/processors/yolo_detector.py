from ultralytics import YOLO
from typing import List, Dict, Tuple
import cv2
import numpy as np
from app.models.asset import DetectedObject


class YOLODetector:
    """Object detection using YOLO26 (Ultralytics)"""
    
    def __init__(self, model_size: str = "yolov8n.pt"):
        """
        Initialize YOLO detector
        
        Args:
            model_size: Model size (yolov8n.pt for nano, yolov8s.pt for small, etc.)
                        In production, use yolov10 or yolov26 when available
        """
        try:
            # Load pre-trained YOLO model
            # Using YOLOv8 as YOLO26 may not be available yet
            # Will upgrade to YOLO26 when released
            self.model = YOLO(model_size)
            self.model.to('cpu')  # Use CPU for compatibility
            print(f"YOLO model loaded: {model_size}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None
    
    def detect_objects(
        self,
        image_path: str,
        confidence_threshold: float = 0.5,
        target_classes: List[str] = None
    ) -> List[DetectedObject]:
        """
        Detect objects in an image
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detection
            target_classes: List of specific classes to detect (None for all)
            
        Returns:
            List of DetectedObject with bounding boxes and labels
        """
        if not self.model:
            return []
        
        try:
            # Run inference
            results = self.model(image_path, conf=confidence_threshold, verbose=False)
            
            detected_objects = []
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get class name
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    # Filter by target classes if specified
                    if target_classes and class_name not in target_classes:
                        continue
                    
                    # Get confidence
                    confidence = float(box.conf[0])
                    
                    # Get bounding box coordinates (x1, y1, x2, y2)
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    
                    detected_objects.append(
                        DetectedObject(
                            label=class_name,
                            confidence=confidence,
                            bbox=bbox
                        )
                    )
            
            return detected_objects
            
        except Exception as e:
            print(f"Error during object detection: {e}")
            return []
    
    def detect_people(self, image_path: str, confidence_threshold: float = 0.5) -> List[DetectedObject]:
        """Detect people specifically in an image"""
        return self.detect_objects(image_path, confidence_threshold, target_classes=['person'])
    
    def detect_logos_brands(self, image_path: str, confidence_threshold: float = 0.5) -> List[DetectedObject]:
        """
        Detect potential logos/brand elements
        Note: This uses general object detection. For specific logo detection,
        custom training on logo datasets is required.
        """
        # COCO classes that might indicate branding
        brand_related_classes = [
            'person',  # People with branded clothing
            'laptop',  # Brand logos on devices
            'cell phone',  # Brand logos on phones
            'bottle',  # Branded bottles
            'cup',  # Branded cups
            'book',  # Branded materials
            'tv',  # Screens with branding
            'monitor'  # Screens with branding
        ]
        
        return self.detect_objects(image_path, confidence_threshold, target_classes=brand_related_classes)
    
    def count_people(self, image_path: str, confidence_threshold: float = 0.5) -> int:
        """Count number of people in an image"""
        people = self.detect_people(image_path, confidence_threshold)
        return len(people)
    
    def get_dominant_objects(self, image_path: str, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Get the most frequently detected objects
        
        Args:
            image_path: Path to image file
            top_n: Number of top objects to return
            
        Returns:
            List of (class_name, count) tuples
        """
        objects = self.detect_objects(image_path)
        
        # Count occurrences
        object_counts = {}
        for obj in objects:
            object_counts[obj.label] = object_counts.get(obj.label, 0) + 1
        
        # Sort by count and return top N
        sorted_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_objects[:top_n]
    
    def draw_detections(
        self,
        image_path: str,
        output_path: str,
        detections: List[DetectedObject]
    ) -> bool:
        """
        Draw bounding boxes on image and save
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image
            detections: List of DetectedObject to draw
            
        Returns:
            bool: True if successful
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Draw bounding boxes
            for detection in detections:
                x1, y1, x2, y2 = map(int, detection.bbox)
                
                # Draw rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{detection.label}: {detection.confidence:.2f}"
                cv2.putText(
                    image,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
            
            # Save image
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error drawing detections: {e}")
            return False


# Singleton instance
yolo_detector = YOLODetector()
