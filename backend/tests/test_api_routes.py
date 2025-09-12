"""
Unit tests for API routes.

Tests the API endpoints including AI integration,
validation, and error handling.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock external dependencies before importing app
with patch.dict('sys.modules', {
    'flask_cors': Mock(),
    'openai': Mock(),
    'anthropic': Mock(),
}):
    from app import create_app


# Use the app and client fixtures from conftest.py


class TestHealthEndpoints:
    """Test health and basic endpoints."""
    
    def test_index_endpoint(self, client):
        """Test index endpoint."""
        response = client.get('/api/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "A-Impact" in data["message"]
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"


class TestQuestionsEndpoint:
    """Test questions endpoint."""
    
    def test_get_questions_success(self, client):
        """Test successful questions retrieval."""
        with patch('app.api.routes.load_features_from_json') as mock_load_features:
            with patch('app.api.routes.create_questionnaire_from_json') as mock_create_questionnaire:
                mock_load_features.return_value = {"feature1": "data1"}
                mock_create_questionnaire.return_value = (
                    [{"name": "test", "type": "text"}],
                    {"version": "1.0"}
                )
                
                response = client.get('/api/questions')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert "questions" in data
                assert "metadata" in data


class TestAnalyzeEndpoint:
    """Test analyze endpoint."""
    
    def test_analyze_missing_data(self, client):
        """Test analyze endpoint with missing data."""
        response = client.post('/api/analyze', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Validation error" in data["error"]
    
    def test_analyze_invalid_data(self, client):
        """Test analyze endpoint with invalid data."""
        invalid_data = {
            "size_m2": -10,  # Invalid negative size
            "seats": 50
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_analyze_success(self, client):
        """Test successful analysis."""
        with patch('app.api.routes.match_requirements') as mock_match:
            with patch('app.api.routes.assess_business_risk_factors') as mock_assess:
                with patch('app.api.routes.generate_recommendations') as mock_recommend:
                    mock_match.return_value = {
                        "matched_requirements": [],
                        "by_category": {},
                        "feature_coverage": [],
                        "total_matches": 0,
                        "user_profile": {"size_m2": 150, "seats": 50},
                        "summary": {
                            "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False},
                            "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
                            "avg_relevance": 0.5
                        }
                    }
                    mock_assess.return_value = []
                    mock_recommend.return_value = {}
                    
                    valid_data = {
                        "size_m2": 150,
                        "seats": 50,
                        "attributes": ["גז"]
                    }
                    
                    response = client.post('/api/analyze', json=valid_data)
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert "business_analysis" in data
                    assert "regulatory_analysis" in data


class TestAIAnalysisEndpoints:
    """Test AI analysis endpoints."""
    
    def test_generate_ai_report_missing_data(self, client):
        """Test AI report generation with missing data."""
        response = client.post('/api/generate-ai-report', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Validation error" in data["error"]
    
    def test_generate_ai_report_success(self, client):
        """Test successful AI report generation."""
        with patch('app.api.routes.match_requirements') as mock_match:
            with patch('app.api.routes.generate_ai_report') as mock_ai:
                mock_match.return_value = {
                    "matched_requirements": [],
                    "by_category": {},
                    "feature_coverage": [],
                    "total_matches": 0,
                    "summary": {
                        "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False},
                        "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
                        "avg_relevance": 0.5
                    },
                    "user_profile": {"size_m2": 150, "seats": 50}
                }
                mock_ai.return_value = Mock(
                    success=True,
                    content="AI Generated Report",
                    provider=Mock(value="openai"),
                    model_used="gpt-4o-mini",
                    tokens_used=100
                )
                
                valid_data = {
                    "size_m2": 150,
                    "seats": 50,
                    "attributes": ["גז"]
                }
                
                response = client.post('/api/generate-ai-report', json=valid_data)
                assert response.status_code == 200
                data = json.loads(response.data)
                assert "ai_report" in data
                assert data["ai_report"]["content"] == "AI Generated Report"
    
    def test_generate_ai_report_ai_failure(self, client):
        """Test AI report generation when AI fails."""
        with patch('app.api.routes.match_requirements') as mock_match:
            with patch('app.api.routes.generate_ai_report') as mock_ai:
                mock_match.return_value = {
                    "matched_requirements": [],
                    "by_category": {},
                    "feature_coverage": [],
                    "total_matches": 0,
                    "summary": {
                        "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False},
                        "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
                        "avg_relevance": 0.5
                    },
                    "user_profile": {"size_m2": 150, "seats": 50}
                }
                mock_ai.return_value = Mock(
                    success=False,
                    error_message="OpenAI API key not found"
                )
                
                valid_data = {
                    "size_m2": 150,
                    "seats": 50,
                    "attributes": ["גז"]
                }
                
                response = client.post('/api/generate-ai-report', json=valid_data)
                assert response.status_code == 500
                data = json.loads(response.data)
                assert "AI report generation failed" in data["error"]
    
    def test_generate_ai_report_checklist_type(self, client):
        """Test AI report generation with checklist type."""
        with patch('app.api.routes.match_requirements') as mock_match:
            with patch('app.api.routes.generate_ai_report') as mock_ai:
                mock_match.return_value = {
                    "matched_requirements": [],
                    "by_category": {},
                    "feature_coverage": [],
                    "total_matches": 0,
                    "summary": {
                        "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False},
                        "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
                        "avg_relevance": 0.5
                    },
                    "user_profile": {"size_m2": 150, "seats": 50}
                }
                mock_ai.return_value = Mock(
                    success=True,
                    content="Checklist Report",
                    provider=Mock(value="openai"),
                    model_used="gpt-4o-mini",
                    tokens_used=50
                )
                
                valid_data = {
                    "size_m2": 150,
                    "seats": 50,
                    "attributes": ["גז"],
                    "report_type": "checklist"
                }
                
                response = client.post('/api/generate-ai-report', json=valid_data)
                assert response.status_code == 200
                mock_ai.assert_called_once()
                # Verify the report_type was passed correctly
                call_args = mock_ai.call_args
                assert call_args[0][1] == "checklist"  # Second argument should be report_type
    
    def test_analyze_with_ai_success(self, client):
        """Test analyze with AI endpoint success."""
        with patch('app.api.routes.match_requirements') as mock_match:
            with patch('app.api.routes.generate_ai_report') as mock_ai:
                with patch('app.api.routes.assess_business_risk_factors') as mock_assess:
                    with patch('app.api.routes.generate_recommendations') as mock_recommend:
                        mock_match.return_value = {
                            "matched_requirements": [],
                            "by_category": {},
                            "feature_coverage": [],
                            "total_matches": 0,
                            "user_profile": {"size_m2": 150, "seats": 50},
                            "summary": {
                                "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False},
                                "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
                                "avg_relevance": 0.5
                            }
                        }
                        # Create a more realistic mock for AI response
                        ai_response_mock = Mock()
                        ai_response_mock.success = True
                        ai_response_mock.content = "AI Analysis Report"
                        ai_response_mock.provider = Mock()
                        ai_response_mock.provider.value = "openai"
                        ai_response_mock.model_used = "gpt-4o-mini"
                        ai_response_mock.tokens_used = 200
                        ai_response_mock.error_message = None
                        mock_ai.return_value = ai_response_mock
                        mock_assess.return_value = []
                        mock_recommend.return_value = {}
                        
                        valid_data = {
                            "size_m2": 150,
                            "seats": 50,
                            "attributes": ["גז"]
                        }
                        
                        response = client.post('/api/analyze-with-ai', json=valid_data)
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert "ai_report" in data
                        assert "business_analysis" in data
                        assert "regulatory_analysis" in data


class TestAIProvidersEndpoint:
    """Test AI providers endpoint."""
    
    def test_get_ai_providers(self, client):
        """Test getting AI providers information."""
        with patch('app.api.routes.ai_service') as mock_service:
            with patch('app.api.routes._get_provider_description') as mock_desc:
                # Create realistic mock objects
                openai_provider = Mock()
                openai_provider.value = "openai"
                
                mock_strategy = Mock()
                mock_strategy.is_available.return_value = True
                
                mock_desc.return_value = "OpenAI GPT - מודל שפה מתקדם עם תמיכה בעברית"
                
                # Create a simple object that behaves like a provider
                class MockProvider:
                    def __init__(self, value):
                        self.value = value
                    
                    def __hash__(self):
                        return hash(self.value)
                    
                    def __eq__(self, other):
                        return isinstance(other, MockProvider) and self.value == other.value
                
                provider = MockProvider("openai")
                
                mock_service.get_available_providers.return_value = [provider]
                mock_service.provider_order = [provider]
                mock_service.strategies = {provider: mock_strategy}
            
            response = client.get('/api/ai-providers')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "available_providers" in data
            assert "provider_details" in data


class TestPreviewFeaturesEndpoint:
    """Test preview features endpoint."""
    
    def test_preview_features_success(self, client):
        """Test successful features preview."""
        with patch('app.api.routes.get_applicable_features') as mock_get_features:
            mock_get_features.return_value = ["feature1", "feature2"]
            
            response = client.post('/api/preview-features', json={"size_m2": 150})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "applicable_features" in data
            assert len(data["applicable_features"]) == 2


class TestErrorHandling:
    """Test error handling in API endpoints."""
    
    def test_analyze_server_error(self, client):
        """Test analyze endpoint with server error."""
        with patch('app.api.routes.match_requirements') as mock_match:
            mock_match.side_effect = Exception("Database error")
            
            valid_data = {
                "size_m2": 150,
                "seats": 50,
                "attributes": ["גז"]
            }
            
            response = client.post('/api/analyze', json=valid_data)
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
    
    def test_ai_report_server_error(self, client):
        """Test AI report generation with server error."""
        with patch('app.api.routes.match_requirements') as mock_match:
            mock_match.side_effect = Exception("AI service error")
            
            valid_data = {
                "size_m2": 150,
                "seats": 50,
                "attributes": ["גז"]
            }
            
            response = client.post('/api/generate-ai-report', json=valid_data)
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data


class TestDataValidation:
    """Test data validation in API endpoints."""
    
    def test_validate_size_m2_range(self, client):
        """Test size_m2 validation range."""
        # Test negative size
        invalid_data = {
            "size_m2": -10,
            "seats": 50
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
        
        # Test too large size
        invalid_data = {
            "size_m2": 50000,
            "seats": 50
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
    
    def test_validate_seats_range(self, client):
        """Test seats validation range."""
        # Test negative seats
        invalid_data = {
            "size_m2": 150,
            "seats": -5
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
        
        # Test too many seats
        invalid_data = {
            "size_m2": 150,
            "seats": 2000
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
    
    def test_validate_required_fields(self, client):
        """Test required fields validation."""
        # Missing size_m2
        invalid_data = {
            "seats": 50
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
        
        # Missing seats
        invalid_data = {
            "size_m2": 150
        }
        response = client.post('/api/analyze', json=invalid_data)
        assert response.status_code == 400
