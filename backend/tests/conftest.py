"""
Pytest configuration and fixtures for backend tests.

Provides common fixtures and test configuration
for all backend unit tests.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch
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


@pytest.fixture(scope="session")
def app():
    """Create test Flask application."""
    # Create temporary directory for test data
    test_dir = tempfile.mkdtemp()
    
    # Set test environment variables
    test_env = {
        'FLASK_ENV': 'testing',
        'TESTING': 'True',
        'OPENAI_API_KEY': 'test-key-for-testing',
        'AI_MAX_TOKENS': '1000',
        'AI_TEMPERATURE': '0.5'
    }
    
    # Mock external dependencies
    with patch.dict('sys.modules', {
        'flask_cors': Mock(),
        'openai': Mock(),
        'anthropic': Mock(),
    }):
        with patch.dict(os.environ, test_env):
            app = create_app()
            app.config.update({
                'TESTING': True,
                'WTF_CSRF_ENABLED': False,
            })
            yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_business_data():
    """Sample business data for testing."""
    return {
        "size_m2": 150,
        "seats": 50,
        "attributes": ["גז", "בשר", "מצלמות אבטחה"],
        "matched_requirements": [
            {
                "category": "בטיחות",
                "paragraph_number": "1.1",
                "text": "עסק המגיש בשר חייב להחזיק תעודת כשרות",
                "priority": "high",
                "relevance_score": 0.9
            },
            {
                "category": "כיבוי אש",
                "paragraph_number": "2.3",
                "text": "עסק המשתמש בגז חייב להתקין גלאי גז",
                "priority": "high",
                "relevance_score": 0.8
            }
        ],
        "by_category": {
            "בטיחות": [
                {
                    "category": "בטיחות",
                    "paragraph_number": "1.1",
                    "text": "עסק המגיש בשר חייב להחזיק תעודת כשרות",
                    "priority": "high",
                    "relevance_score": 0.9
                }
            ],
            "כיבוי אש": [
                {
                    "category": "כיבוי אש",
                    "paragraph_number": "2.3",
                    "text": "עסק המשתמש בגז חייב להתקין גלאי גז",
                    "priority": "high",
                    "relevance_score": 0.8
                }
            ]
        },
        "summary": {
            "business_profile": {
                "size_category": "large",
                "occupancy_category": "high",
                "special_requirements": True
            },
            "priority_breakdown": {
                "high": 2,
                "medium": 0,
                "low": 0
            },
            "avg_relevance": 0.85
        }
    }


@pytest.fixture
def sample_user_input():
    """Sample user input for testing."""
    return {
        "size_m2": 150,
        "seats": 50,
        "attributes": ["גז", "בשר"],
        "uses_gas": True,
        "serves_meat": True
    }


@pytest.fixture
def sample_questions():
    """Sample questions for testing."""
    return [
        {
            "name": "size_m2",
            "label": "גודל העסק (מ\"ר)",
            "type": "number",
            "required": True,
            "min": 1,
            "max": 10000,
            "placeholder": "לדוגמה: 150",
            "description": "שטח העסק במטרים מרובעים"
        },
        {
            "name": "seats",
            "label": "מספר מקומות ישיבה / תפוסה",
            "type": "number",
            "required": True,
            "min": 0,
            "max": 1000,
            "placeholder": "לדוגמה: 50",
            "description": "מספר לקוחות שיכולים לשבת במקום"
        },
        {
            "name": "attributes",
            "label": "מאפייני עסק נוספים",
            "type": "multiselect",
            "required": False,
            "options": [
                {"value": "גז", "label": "שימוש בגז"},
                {"value": "בשר", "label": "הגשת בשר"},
                {"value": "מצלמות אבטחה", "label": "מצלמות אבטחה"}
            ],
            "description": "בחר את כל המאפיינים הרלוונטיים"
        }
    ]


@pytest.fixture
def sample_matching_result():
    """Sample matching result for testing."""
    return {
        "matched_requirements": [
            {
                "category": "בטיחות",
                "paragraph_number": "1.1",
                "text": "דרישת בטיחות חשובה",
                "priority": "high",
                "relevance_score": 0.9
            }
        ],
        "by_category": {
            "בטיחות": [
                {
                    "category": "בטיחות",
                    "paragraph_number": "1.1",
                    "text": "דרישת בטיחות חשובה",
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
            "priority_breakdown": {
                "high": 1,
                "medium": 0,
                "low": 0
            },
            "avg_relevance": 0.9,
            "business_profile": {
                "size_category": "large",
                "occupancy_category": "high",
                "special_requirements": True
            }
        }
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return Mock(
        choices=[
            Mock(
                message=Mock(
                    content="דוח AI מפורט עם המלצות מותאמות אישית"
                )
            )
        ],
        usage=Mock(
            total_tokens=150
        )
    )


@pytest.fixture
def mock_ai_response_success():
    """Mock successful AI response."""
    from app.services.ai_service import AIResponse, AIProvider
    
    return AIResponse(
        content="דוח AI מפורט עם המלצות מותאמות אישית",
        provider=AIProvider.OPENAI,
        success=True,
        tokens_used=150,
        model_used="gpt-4o-mini"
    )


@pytest.fixture
def mock_ai_response_failure():
    """Mock failed AI response."""
    from app.services.ai_service import AIResponse, AIProvider
    
    return AIResponse(
        content="",
        provider=AIProvider.OPENAI,
        success=False,
        error_message="OpenAI API key not found"
    )


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables for all tests."""
    test_env = {
        'OPENAI_API_KEY': 'test-key-for-testing',
        'AI_MAX_TOKENS': '1000',
        'AI_TEMPERATURE': '0.5',
        'FLASK_ENV': 'testing'
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        yield


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('app.api.helpers.Path.open') as mock_open:
        with patch('app.api.helpers.json.load') as mock_json_load:
            yield mock_open, mock_json_load


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as requiring AI service"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Mark AI service tests
        if "ai_service" in item.nodeid:
            item.add_marker(pytest.mark.ai)
        
        # Mark API route tests as integration tests
        if "test_api_routes" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark other tests as unit tests
        else:
            item.add_marker(pytest.mark.unit)