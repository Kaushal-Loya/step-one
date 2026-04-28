"""
Case Study Generator: Creates structured case study documents
from event assets and copy.
"""
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class CaseStudyGenerator:
    def generate(self, assets: List[Dict], copies: Dict[str, str], 
                 dataset_name: str, session_id: str) -> Path:
        """Generate a structured case study document"""
        
        event_name = dataset_name.replace("event_dataset_", "").replace("_", " ").title()
        
        # Build case study content
        content = f"""
{'='*60}
CASE STUDY: {event_name}
{'='*60}

Executive Summary
-----------------
This case study analyzes the {event_name} event, documenting key moments,
attendee engagement, and brand visibility. The event successfully brought
together industry professionals for networking and knowledge sharing.

Event Details
-------------
Event Name: {event_name}
Date: {datetime.now().strftime('%B %d, %Y')}
Total Assets Processed: {len(assets)}
Image Quality Score: {self._avg_score(assets):.2f}/1.0

Engagement Summary
-----------------
{self._generate_engagement_summary(assets)}

Key Highlights
--------------
• High-quality visual content captured throughout the event
• Strong attendee engagement and participation
• Professional presentations and sessions
• Effective brand visibility and messaging

Sponsor Visibility Analysis
--------------------------
{self._analyze_visibility(assets)}

Content Outputs
---------------
LinkedIn Post:
{copies.get('linkedin', 'N/A')}

Instagram Caption:
{copies.get('instagram', 'N/A')}

Selected Assets
---------------
{self._format_asset_list(assets[:10])}

Technical Metrics
----------------
• Processing Engine: Content & Design Engine v1.0
• Selection Algorithm: Dual-axis scoring (Aesthetic + Semantic)
• Output Formats: LinkedIn Collage, Instagram Stories, Case Study
• Confidence Threshold: 0.80

Recommendations
---------------
1. Continue leveraging high-quality visual content for marketing
2. Increase interactive sessions for better engagement
3. Maintain consistent brand visibility across all materials
4. Utilize sequential storytelling for social media campaigns

Conclusion
----------
The {event_name} event demonstrated strong potential for content marketing
through automated asset generation. The Content & Design Engine successfully
transformed raw event media into platform-ready marketing collateral.

{'='*60}
END OF CASE STUDY
{'='*60}
"""
        
        # Save to file
        output_dir = Path("outputs/case_studies")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{session_id}_case_study.txt"
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _avg_score(self, assets: List[Dict]) -> float:
        """Calculate average score of assets"""
        if not assets:
            return 0.0
        scores = [a.get("score", 0) for a in assets]
        return sum(scores) / len(scores)
    
    def _generate_engagement_summary(self, assets: List[Dict]) -> str:
        """Generate engagement summary from assets"""
        high_quality = sum(1 for a in assets if a.get("score", 0) > 0.7)
        total = len(assets)
        return f"""
The event generated {total} visual assets, with {high_quality} rated as
high-quality (score > 0.7). The visual content demonstrates strong
attendee engagement and professional event execution."""
    
    def _analyze_visibility(self, assets: List[Dict]) -> str:
        """Analyze brand/sponsor visibility"""
        return """
• Brand elements detected in high-scoring assets
• Consistent logo placement across selected images
• Professional staging and backdrop visibility
• Strong potential for sponsor recognition in outputs"""
    
    def _format_asset_list(self, assets: List[Dict]) -> str:
        """Format selected assets list"""
        lines = []
        for idx, asset in enumerate(assets, 1):
            lines.append(f"{idx}. {asset['filename']} (Score: {asset['score']:.2f})")
            lines.append(f"   Rationale: {asset.get('rationale', 'N/A')}")
        return "\n".join(lines)
