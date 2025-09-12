"""
Integration tests for the licensing assistant backend.

Tests the complete flow from API endpoints through
business logic to AI integration.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

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


class TestCompleteWorkflow:
    """Test complete workflow from input to AI report."""
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    @patch('app.api.routes.match_requirements')
    @patch('app.api.routes.generate_ai_report')
    def test_complete_analyze_with_ai_workflow(self, mock_ai, mock_match, mock_features, mock_questions, client):
        """Test complete analyze-with-AI workflow."""
        # Mock questions loading
        mock_questions.return_value = {
            "questionnaire": {
                "required_fields": ["size_m2", "seats"],
                "version": "1.1"
            },
            "questions": []
        }
        
        # Mock features loading
        mock_features.return_value = {
            "גז": {"keywords": ["גז"]},
            "בשר": {"keywords": ["בשר"]}
        }
        
        # Mock matching result
        mock_match.return_value = {
            "matched_requirements": [
                {
                    "category": "בטיחות",
                    "paragraph_number": "1.1",
                    "text": "דרישת בטיחות",
                    "priority": "high",
                    "relevance_score": 0.9
                }
            ],
            "by_category": {
                "בטיחות": [
                    {
                        "category": "בטיחות",
                        "paragraph_number": "1.1",
                        "text": "דרישת בטיחות",
                        "priority": "high",
                        "relevance_score": 0.9
                    }
                ]
            },
            "feature_coverage": ["מ\"ר", "תפוסה", "גז"],
            "user_profile": {
                "size_m2": 150,
                "seats": 50,
                "attributes": ["גז"],
                "uses_gas": True,
                "serves_meat": False
            },
            "total_matches": 1,
            "summary": {
                "categories_count": 1,
                "priority_breakdown": {"high": 1, "medium": 0, "low": 0},
                "avg_relevance": 0.9,
                "business_profile": {
                    "size_category": "large",
                    "occupancy_category": "high",
                    "special_requirements": True
                }
            }
        }
        
        # Mock AI response - create realistic mock
        ai_response_mock = Mock()
        ai_response_mock.success = True
        ai_response_mock.content = "דוח AI מפורט עם המלצות"
        ai_response_mock.provider = Mock()
        ai_response_mock.provider.value = "openai"
        ai_response_mock.model_used = "gpt-4o-mini"
        ai_response_mock.tokens_used = 150
        ai_response_mock.error_message = None
        mock_ai.return_value = ai_response_mock
        
        # Test data
        test_data = {
            "size_m2": 150,
            "seats": 50,
            "attributes": ["גז"]
        }
        
        # Make request
        response = client.post('/api/analyze-with-ai', json=test_data)
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check response structure
        assert "user_input" in data
        assert "business_analysis" in data
        assert "regulatory_analysis" in data
        assert "feature_coverage" in data
        assert "recommendations" in data
        assert "ai_report" in data
        assert "analysis_metadata" in data
        
        # Check AI report
        ai_report = data["ai_report"]
        assert ai_report["success"] is True
        assert ai_report["content"] == "דוח AI מפורט עם המלצות"
        assert ai_report["provider"] == "openai"
        
        # Verify mocks were called
        mock_match.assert_called_once()
        mock_ai.assert_called_once()
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    @patch('app.api.routes.match_requirements')
    @patch('app.api.routes.generate_ai_report')
    def test_ai_report_generation_workflow(self, mock_ai, mock_match, mock_features, mock_questions, client):
        """Test AI report generation workflow."""
        # Mock dependencies
        mock_questions.return_value = {"questionnaire": {"required_fields": ["size_m2", "seats"]}}
        mock_features.return_value = {}
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
            "user_profile": {"size_m2": 200, "seats": 75}
        }
        mock_ai.return_value = Mock(
            success=True,
            content="דוח AI מפורט",
            provider=Mock(value="openai"),
            model_used="gpt-4o-mini",
            tokens_used=100
        )
        
        # Test data
        test_data = {
            "size_m2": 200,
            "seats": 75,
            "attributes": ["בשר"],
            "report_type": "checklist"
        }
        
        # Make request
        response = client.post('/api/generate-ai-report', json=test_data)
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert "ai_report" in data
        assert data["ai_report"]["content"] == "דוח AI מפורט"
        assert data["ai_report"]["provider"] == "openai"
        assert data["ai_report"]["model_used"] == "gpt-4o-mini"
        
        # Verify AI was called with correct report type
        call_args = mock_ai.call_args
        assert call_args[0][1] == "checklist"  # report_type parameter


class TestErrorHandlingIntegration:
    """Test error handling in complete workflows."""
    
    @patch('app.api.routes.load_questions_from_json')
    def test_validation_error_handling(self, mock_questions, client):
        """Test validation error handling in complete workflow."""
        mock_questions.return_value = {
            "questionnaire": {"required_fields": ["size_m2", "seats"]},
            "validation": {
                "size_m2": {"min": 1, "max": 10000},
                "seats": {"min": 0, "max": 1000}
            }
        }
        
        # Invalid data
        invalid_data = {
            "size_m2": -10,  # Invalid negative size
            "seats": 50
        }
        
        response = client.post('/api/analyze-with-ai', json=invalid_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Validation error" in data["error"]
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    @patch('app.api.routes.match_requirements')
    @patch('app.api.routes.generate_ai_report')
    def test_ai_service_error_handling(self, mock_ai, mock_match, mock_features, mock_questions, client):
        """Test AI service error handling in complete workflow."""
        # Mock successful dependencies
        mock_questions.return_value = {"questionnaire": {"required_fields": ["size_m2", "seats"]}}
        mock_features.return_value = {}
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
        
        # Mock AI failure
        mock_ai.return_value = Mock(
            success=False,
            error_message="OpenAI API key not found"
        )
        
        test_data = {
            "size_m2": 150,
            "seats": 50,
            "attributes": []
        }
        
        response = client.post('/api/generate-ai-report', json=test_data)
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "AI report generation failed" in data["error"]
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    def test_matching_service_error_handling(self, mock_features, mock_questions, client):
        """Test matching service error handling."""
        mock_questions.return_value = {"questionnaire": {"required_fields": ["size_m2", "seats"]}}
        mock_features.return_value = {}
        
        with patch('app.api.routes.match_requirements') as mock_match:
            mock_match.side_effect = Exception("Matching service error")
            
            test_data = {
                "size_m2": 150,
                "seats": 50,
                "attributes": []
            }
            
            response = client.post('/api/analyze', json=test_data)
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data


class TestDataFlowIntegration:
    """Test data flow through the system."""
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    @patch('app.api.routes.match_requirements')
    def test_data_transformation_flow(self, mock_match, mock_features, mock_questions, client):
        """Test data transformation through the system."""
        # Mock dependencies
        mock_questions.return_value = {
            "questionnaire": {"required_fields": ["size_m2", "seats"]},
            "validation": {
                "size_m2": {"min": 1, "max": 10000},
                "seats": {"min": 0, "max": 1000}
            }
        }
        mock_features.return_value = {
            "גז": {"keywords": ["גז"]},
            "בשר": {"keywords": ["בשר"]}
        }
        
        # Mock matching with specific data structure
        mock_match.return_value = {
            "matched_requirements": [
                {
                    "category": "בטיחות",
                    "paragraph_number": "1.1",
                    "text": "דרישת בטיחות",
                    "priority": "high",
                    "relevance_score": 0.9
                }
            ],
            "by_category": {
                "בטיחות": [
                    {
                        "category": "בטיחות",
                        "paragraph_number": "1.1",
                        "text": "דרישת בטיחות",
                        "priority": "high",
                        "relevance_score": 0.9
                    }
                ]
            },
            "feature_coverage": ["מ\"ר", "תפוסה", "גז"],
            "user_profile": {
                "size_m2": 150,
                "seats": 50,
                "attributes": ["גז"],
                "uses_gas": True,
                "serves_meat": False
            },
            "total_matches": 1,
            "summary": {
                "categories_count": 1,
                "priority_breakdown": {"high": 1, "medium": 0, "low": 0},
                "avg_relevance": 0.9,
                "business_profile": {
                    "size_category": "large",
                    "occupancy_category": "high",
                    "special_requirements": True
                }
            }
        }
        
        # Test data
        test_data = {
            "size_m2": 150,
            "seats": 50,
            "attributes": ["גז"]
        }
        
        # Make request
        response = client.post('/api/analyze', json=test_data)
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check that data was properly transformed
        assert data["user_input"]["size_m2"] == 150
        assert data["user_input"]["seats"] == 50
        assert data["user_input"]["attributes"] == ["גז"]
        
        # Check business analysis
        business_analysis = data["business_analysis"]
        assert "profile" in business_analysis
        assert "classification" in business_analysis
        assert "risk_factors" in business_analysis
        
        # Check regulatory analysis
        regulatory_analysis = data["regulatory_analysis"]
        assert "matched_requirements" in regulatory_analysis
        assert "by_category" in regulatory_analysis
        assert "total_matches" in regulatory_analysis
        assert regulatory_analysis["total_matches"] == 1
        
        # Verify matching was called with correct data
        call_args = mock_match.call_args[0][0]  # First argument (user_answers)
        assert call_args["size_m2"] == 150
        assert call_args["seats"] == 50
        assert call_args["attributes"] == ["גז"]


class TestAIProviderIntegration:
    """Test AI provider integration."""
    
    @patch('app.api.routes.ai_service')
    def test_ai_providers_endpoint(self, mock_ai_service, client):
        """Test AI providers endpoint."""
        with patch('app.api.routes._get_provider_description') as mock_desc:
            # Create realistic mock objects
            class MockProvider:
                def __init__(self, value):
                    self.value = value
                
                def __hash__(self):
                    return hash(self.value)
                
                def __eq__(self, other):
                    return isinstance(other, MockProvider) and self.value == other.value
            
            provider = MockProvider("openai")
            
            mock_strategy = Mock()
            mock_strategy.is_available.return_value = True
            
            mock_desc.return_value = "OpenAI GPT - מודל שפה מתקדם עם תמיכה בעברית"
            
            mock_ai_service.get_available_providers.return_value = [provider]
            mock_ai_service.provider_order = [provider]
            mock_ai_service.strategies = {provider: mock_strategy}
        
        response = client.get('/api/ai-providers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert "available_providers" in data
        assert "provider_details" in data
        assert "openai" in data["available_providers"]
        
        # Verify service was called
        mock_ai_service.get_available_providers.assert_called_once()
    
    @patch('app.api.routes.ai_service')
    def test_ai_providers_unavailable(self, mock_ai_service, client):
        """Test AI providers endpoint when no providers available."""
        mock_ai_service.get_available_providers.return_value = []
        mock_ai_service.provider_order = []
        mock_ai_service.strategies = {}
        
        response = client.get('/api/ai-providers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["available_providers"] == []
        assert data["provider_details"] == {}


class TestPerformanceIntegration:
    """Test performance aspects of integration."""
    
    @patch('app.api.routes.load_questions_from_json')
    @patch('app.api.routes.load_features_from_json')
    @patch('app.api.routes.match_requirements')
    def test_large_dataset_handling(self, mock_match, mock_features, mock_questions, client):
        """Test handling of large datasets."""
        # Mock large dataset
        large_requirements = [
            {
                "category": "בטיחות",
                "paragraph_number": f"{i}.1",
                "text": f"דרישת בטיחות {i}",
                "priority": "high" if i % 3 == 0 else "medium",
                "relevance_score": 0.8
            }
            for i in range(100)  # Large number of requirements
        ]
        
        mock_questions.return_value = {"questionnaire": {"required_fields": ["size_m2", "seats"]}}
        mock_features.return_value = {}
        mock_match.return_value = {
            "matched_requirements": large_requirements,
            "by_category": {"בטיחות": large_requirements},
            "feature_coverage": [],
            "user_profile": {"size_m2": 150, "seats": 50},
            "total_matches": 100,
            "summary": {
                "categories_count": 1,
                "priority_breakdown": {"high": 33, "medium": 67, "low": 0},
                "avg_relevance": 0.8,
                "business_profile": {"size_category": "large", "occupancy_category": "high", "special_requirements": False}
            }
        }
        
        test_data = {
            "size_m2": 150,
            "seats": 50,
            "attributes": []
        }
        
        response = client.post('/api/analyze', json=test_data)
        
        # Should handle large dataset without issues
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["regulatory_analysis"]["total_matches"] == 100
