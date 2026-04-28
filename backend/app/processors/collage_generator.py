"""
Collage Generator: Creates LinkedIn post collages from selected images.
"""
from PIL import Image
from pathlib import Path
from typing import List, Dict

class CollageGenerator:
    def create_linkedin_collage(self, assets: List[Dict], session_id: str) -> Path:
        """Create a 4-6 image collage for LinkedIn"""
        selected = assets[:6]
        num_images = len(selected)
        
        if num_images == 0:
            raise ValueError("No assets provided")
        
        if num_images <= 2:
            cols, rows = num_images, 1
        elif num_images <= 4:
            cols, rows = 2, 2
        else:
            cols, rows = 3, 2
        
        canvas_width = 1200
        canvas_height = 1200
        padding = 10
        
        cell_width = (canvas_width - (cols + 1) * padding) // cols
        cell_height = (canvas_height - (rows + 1) * padding) // rows
        
        collage = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
        
        for idx, asset in enumerate(selected):
            img_path = asset["path"]
            try:
                img = Image.open(img_path)
                img = self._resize_to_fit(img, cell_width, cell_height)
                
                col = idx % cols
                row = idx // cols
                x = padding + col * (cell_width + padding) + (cell_width - img.width) // 2
                y = padding + row * (cell_height + padding) + (cell_height - img.height) // 2
                
                collage.paste(img, (x, y))
            
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue
        
        output_dir = Path("outputs/linkedin")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{session_id}_collage.jpg"
        collage.save(output_path, "JPEG", quality=95)
        
        return output_path
    
    def _resize_to_fit(self, img: Image, target_width: int, target_height: int) -> Image:
        """Resize image to fit target dimensions while maintaining aspect ratio"""
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * img_ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
