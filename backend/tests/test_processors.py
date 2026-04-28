import pytest
from app.processors.metadata_extractor import MetadataExtractor
from app.processors.normalizer import MediaNormalizer
from app.processors.asset_selector import AssetSelector
from app.processors.aesthetic_scorer import AestheticScorer


def test_metadata_extractor():
    """Test metadata extraction"""
    extractor = MetadataExtractor()
    assert extractor is not None


def test_media_normalizer():
    """Test media normalizer"""
    normalizer = MediaNormalizer()
    assert normalizer is not None


def test_asset_selector():
    """Test asset selector"""
    selector = AssetSelector()
    
    # Test with mock data
    mock_assets = [
        {
            "analysis": {
                "aesthetic_score": 0.8,
                "energy_score": 0.7,
                "emotions": {"happy": 0.5, "neutral": 0.5},
                "detected_objects": [{"label": "person"}]
            }
        }
    ]
    
    result = selector.select_assets_for_session(mock_assets)
    assert result is not None
    assert "categorized_assets" in result
    assert "statistics" in result


def test_aesthetic_scorer():
    """Test aesthetic scorer"""
    scorer = AestheticScorer()
    assert scorer is not None


def test_composite_score_calculation():
    """Test composite score calculation"""
    selector = AssetSelector()
    
    mock_asset = {
        "analysis": {
            "aesthetic_score": 0.8,
            "energy_score": 0.7,
            "emotions": {"happy": 0.5, "neutral": 0.5},
            "detected_objects": [{"label": "person"}]
        }
    }
    
    score = selector.calculate_composite_score(mock_asset)
    assert 0 <= score <= 1
