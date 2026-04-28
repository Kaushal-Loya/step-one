"""
Copy Generator: Generates platform-specific copy using templates
and basic NLP. Integrates with Gemini API if available.
"""
import os
from typing import Dict
from pathlib import Path
import json

class CopyGenerator:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    def generate_all(self, selected_assets: list, dataset_name: str) -> Dict[str, str]:
        """Generate copy for LinkedIn and Instagram"""
        
        # Extract event context from dataset name
        event_name = self._extract_event_name(dataset_name)
        
        # Try Gemini API if available
        if self.gemini_api_key:
            try:
                return self._generate_with_gemini(selected_assets, event_name)
            except Exception as e:
                print(f"Gemini API failed: {e}, falling back to templates")
        
        # Fallback to template-based generation
        return self._generate_with_templates(event_name)
    
    def _extract_event_name(self, dataset_name: str) -> str:
        """Extract readable event name from dataset folder name"""
        name = dataset_name.replace("event_dataset_", "").replace("_", " ")
        return name.title()
    
    def _generate_with_templates(self, event_name: str) -> Dict[str, str]:
        """Generate copy using templates"""
        linkedin = f"""Had an incredible time at {event_name}! 

The energy in the room was amazing, with industry leaders sharing insights and networking opportunities that will shape the future.

Key highlights:
• Engaging presentations from thought leaders
• Valuable networking with industry peers  
• Hands-on workshops and interactive sessions

Events like these remind me why I love being part of this community. Looking forward to implementing these learnings!

#EventRecap #{event_name.replace(' ', '')} #Networking #Innovation"""
        
        instagram = f"""✨ {event_name} vibes! 

What an amazing experience filled with learning, networking, and inspiration! 

Swipe to see the highlights →

#EventLife #{event_name.replace(' ', '')} #GoodTimes #Networking #Innovation"""
        
        return {
            "linkedin": linkedin,
            "instagram": instagram
        }
    
    def _generate_with_gemini(self, selected_assets: list, event_name: str) -> Dict[str, str]:
        """Generate copy using Gemini API"""
        import google.generativeai as genai
        
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # LinkedIn prompt
        linkedin_prompt = f"""Write a professional LinkedIn post about attending {event_name}. 
        Write as if you attended the event. Include 3-4 bullet points of highlights. 
        Tone: Professional, insightful, 200-300 words. 
        Do not use hashtags in the body, add them at the end."""
        
        linkedin_response = model.generate_content(linkedin_prompt)
        
        # Instagram prompt  
        instagram_prompt = f"""Write a casual Instagram caption about {event_name}.
        Tone: Fun, visual, emoji-rich, 100-150 words.
        Start with an emoji. Include hashtags at the end."""
        
        instagram_response = model.generate_content(instagram_prompt)
        
        return {
            "linkedin": linkedin_response.text,
            "instagram": instagram_response.text
        }
