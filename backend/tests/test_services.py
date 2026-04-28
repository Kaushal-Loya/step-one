import pytest
from app.services.mongo_service import MongoDB
from app.services.s3_service import s3_service
from app.services.qa_judge import qa_judge


def test_mongo_singleton():
    """Test MongoDB singleton"""
    db = MongoDB.get_database()
    assert db is not None


def test_s3_service():
    """Test S3 service initialization"""
    assert s3_service is not None
    assert s3_service.bucket is not None


def test_qa_judge():
    """Test QA judge initialization"""
    assert qa_judge is not None


def test_confidence_calculation():
    """Test confidence score calculation"""
    evaluation = {
        "layout_valid": True,
        "semantically_accurate": True,
        "hallucination_detected": False
    }
    
    confidence = qa_judge.calculate_confidence_score(evaluation, 0.85)
    assert 0 <= confidence <= 1


def test_flagging_logic():
    """Test flagging logic"""
    # Should flag for low confidence
    evaluation = {
        "layout_valid": True,
        "semantically_accurate": True,
        "hallucination_detected": False
    }
    confidence = 0.4
    
    should_flag, reason = qa_judge.should_flag_for_review(evaluation, confidence)
    assert should_flag is True
    assert "threshold" in reason.lower()
    
    # Should not flag for high confidence
    confidence = 0.9
    should_flag, reason = qa_judge.should_flag_for_review(evaluation, confidence)
    assert should_flag is False
