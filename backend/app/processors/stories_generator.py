from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Optional
import tempfile
import os


class StoriesGenerator:
    """Generate Instagram Stories from selected assets"""
    
    def __init__(self):
        """Initialize stories generator"""
        self.story_size = (1080, 1920)  # 9:16 aspect ratio
        self.padding = 40
        self.font_size_large = 48
        self.font_size_small = 32
    
    def create_story_frame(
        self,
        image_path: str,
        text_overlay: str,
        output_path: Optional[str] = None,
        gradient_overlay: bool = True
    ) -> Optional[str]:
        """
        Create a single Instagram story frame
        
        Args:
            image_path: Path to background image
            text_overlay: Text to overlay
            output_path: Path to save story frame
            gradient_overlay: Add gradient overlay for text readability
            
        Returns:
            str: Path to generated story frame or None
        """
        try:
            # Load and resize image to story dimensions
            img = Image.open(image_path).convert("RGB")
            img = self._resize_cover(img, self.story_size[0], self.story_size[1])
            
            # Add gradient overlay if enabled
            if gradient_overlay:
                img = self._add_gradient_overlay(img)
            
            # Add text overlay
            img = self._add_text_overlay(img, text_overlay)
            
            # Save output
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.jpg')
            
            img.save(output_path, 'JPEG', quality=90)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating story frame: {e}")
            return None
    
    def create_story_sequence(
        self,
        assets: List[Dict],
        session_id: str,
        s3_service
    ) -> List[Dict]:
        """
        Create sequential Instagram stories from assets
        
        Args:
            assets: List of asset dictionaries with text overlays
            session_id: Session ID
            s3_service: S3 service instance
            
        Returns:
            List of generated story frame info
        """
        generated_frames = []
        
        for i, asset in enumerate(assets):
            try:
                # Download image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    input_path = temp_file.name
                
                s3_service.s3_client.download_file(
                    s3_service.bucket,
                    asset["s3_key"],
                    input_path
                )
                
                # Get text overlay (from asset or generate default)
                text = asset.get("text_overlay", f"Story {i+1}")
                
                # Create story frame
                frame_path = self.create_story_frame(input_path, text)
                
                if frame_path:
                    # Upload to S3
                    frame_key = f"sessions/{session_id}/stories/frame_{i+1}.jpg"
                    s3_service.s3_client.upload_file(
                        frame_path,
                        s3_service.bucket,
                        frame_key,
                        ExtraArgs={'ContentType': 'image/jpeg'}
                    )
                    
                    generated_frames.append({
                        "sequence_order": i,
                        "image_url": s3_service.get_file_url(frame_key),
                        "text_overlay": text,
                        "s3_key": frame_key,
                        "asset_id": asset.get("_id")
                    })
                
                # Clean up
                if os.path.exists(input_path):
                    os.unlink(input_path)
                if frame_path and os.path.exists(frame_path):
                    os.unlink(frame_path)
                    
            except Exception as e:
                print(f"Error creating story frame {i}: {e}")
        
        return generated_frames
    
    def _resize_cover(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize image to cover target dimensions (crop if needed)"""
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider - crop width
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller - crop height
            new_width = target_width
            new_height = int(new_width / img_ratio)
        
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return resized.crop((left, top, right, bottom))
    
    def _add_gradient_overlay(self, image: Image.Image) -> Image.Image:
        """Add bottom gradient overlay for text readability"""
        img = image.convert("RGBA")
        
        # Create gradient overlay
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw gradient from bottom (opaque black) to top (transparent)
        for y in range(img.height):
            alpha = int(255 * (y / img.height) * 0.7)  # 70% max opacity
            if y > img.height // 2:  # Only apply to bottom half
                draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
        
        # Composite
        return Image.alpha_composite(img, overlay).convert("RGB")
    
    def _add_text_overlay(self, image: Image.Image, text: str) -> Image.Image:
        """Add text overlay to image"""
        img = image.convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size_large)
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size_small)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Calculate text position (bottom center)
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        
        x = (img.width - text_width) // 2
        y = img.height - 200  # 200px from bottom
        
        # Draw text with shadow
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font_large, fill=(0, 0, 0, 200))
        draw.text((x, y), text, font=font_large, fill=(255, 255, 255, 255))
        
        return img.convert("RGB")
    
    def create_branded_story(
        self,
        image_path: str,
        brand_name: str,
        event_name: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Create branded story frame with logo and event info
        
        Args:
            image_path: Path to background image
            brand_name: Brand name to display
            event_name: Event name to display
            output_path: Path to save story frame
            
        Returns:
            str: Path to generated story frame or None
        """
        try:
            # Create base story frame
            frame_path = self.create_story_frame(image_path, event_name)
            
            if not frame_path:
                return None
            
            # Load frame and add branding
            img = Image.open(frame_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except:
                font = ImageFont.load_default()
            
            # Add brand name at top
            draw.text((40, 40), brand_name, font=font, fill=(255, 255, 255, 200))
            
            # Save
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.jpg')
            
            img.convert("RGB").save(output_path, 'JPEG', quality=90)
            
            # Clean up original frame
            if os.path.exists(frame_path):
                os.unlink(frame_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating branded story: {e}")
            return None
    
    def create_story_with_swipe_link(
        self,
        image_path: str,
        link_text: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Create story frame with swipe-up link indicator
        
        Args:
            image_path: Path to background image
            link_text: Text for the link
            output_path: Path to save story frame
            
        Returns:
            str: Path to generated story frame or None
        """
        try:
            # Create base story frame
            frame_path = self.create_story_frame(image_path, link_text)
            
            if not frame_path:
                return None
            
            # Load frame and add swipe indicator
            img = Image.open(frame_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # Draw arrow indicator at bottom
            arrow_y = img.height - 100
            arrow_x = img.width // 2
            
            # Draw simple up arrow
            draw.polygon([
                (arrow_x, arrow_y - 20),
                (arrow_x - 15, arrow_y + 10),
                (arrow_x + 15, arrow_y + 10)
            ], fill=(255, 255, 255, 255))
            
            # Draw "Swipe up" text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((arrow_x - 40, arrow_y + 20), "Swipe up", font=font, fill=(255, 255, 255, 255))
            
            # Save
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.jpg')
            
            img.convert("RGB").save(output_path, 'JPEG', quality=90)
            
            # Clean up original frame
            if os.path.exists(frame_path):
                os.unlink(frame_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating story with swipe link: {e}")
            return None


# Singleton instance
stories_generator = StoriesGenerator()
