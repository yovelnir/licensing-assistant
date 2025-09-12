"""
API Helper Functions

This module contains helper functions for the API routes to keep the main routes file clean and organized.
Uses the Single Responsibility Principle to separate concerns.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from app.services.matching import get_applicable_features

# Configure logging
logger = logging.getLogger(__name__)


def load_features_from_json() -> Dict[str, Any]:
    """
    Load features from features.json file for dynamic questionnaire generation.
    
    Returns:
        Dictionary containing feature definitions or empty dict on error
    """
    try:
        features_path = Path("app/data/raw/features.json")
        with features_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load features.json: {e}")
        return {}


def load_questions_from_json() -> Dict[str, Any]:
    """
    Load questions configuration from questions.json file.
    
    Returns:
        Dictionary containing questionnaire configuration or empty dict on error
    """
    try:
        questions_path = Path("app/data/questions.json")
        with questions_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load questions.json: {e}")
        return {}


def load_feature_mappings_from_json() -> Dict[str, Any]:
    """
    Load feature mappings from feature-mappings.json file.
    
    Returns:
        Dictionary containing feature mappings or empty dict on error
    """
    try:
        mappings_path = Path("app/data/feature-mappings.json")
        with mappings_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load feature-mappings.json: {e}")
        return {}


def create_feature_question_options(features_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Create multiselect options from features.json using feature-mappings.json configuration.
    
    Args:
        features_data: Loaded features from features.json
        
    Returns:
        List of option dictionaries for multiselect questions
    """
    options = []
    
    # Load feature mappings from JSON configuration
    mappings_config = load_feature_mappings_from_json()
    feature_mappings = mappings_config.get("feature_mappings", {})
    settings = mappings_config.get("settings", {})
    
    # Check if we should exclude mandatory fields
    exclude_mandatory = settings.get("exclude_mandatory_from_questions", True)
    
    for feature_key, feature_data in features_data.items():
        # Skip mandatory fields if configured to do so
        if exclude_mandatory and feature_key in ["מ\"ר", "תפוסה"]:
            continue
            
        # Get mapping from JSON configuration
        mapping = feature_mappings.get(feature_key, {})
        
        # Skip if explicitly excluded from questions
        if mapping.get("exclude_from_questions", False):
            continue
            
        # Create option with enhanced properties
        option = {
            "value": feature_key,
            "label": mapping.get("label", feature_key),
            "description": mapping.get("description", ""),
            "category": mapping.get("category", "אחר"),
            "priority": mapping.get("priority", settings.get("default_priority", "medium")),
            "icon": mapping.get("icon", "")
        }
        
        options.append(option)
    
    # Sort by priority if configured
    priority_order = {"mandatory": 0, "high": 1, "medium": 2, "low": 3}
    options.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2))
    
    return options


def get_feature_categories() -> Dict[str, Any]:
    """
    Get feature categories from feature-mappings.json.
    
    Returns:
        Dictionary containing category definitions
    """
    mappings_config = load_feature_mappings_from_json()
    return mappings_config.get("categories", {})


def get_feature_mapping_settings() -> Dict[str, Any]:
    """
    Get feature mapping settings from feature-mappings.json.
    
    Returns:
        Dictionary containing mapping settings
    """
    mappings_config = load_feature_mappings_from_json()
    return mappings_config.get("settings", {})


def validate_user_input(payload: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    """
    Validate user input for the analyze endpoint using questions.json configuration.
    
    Args:
        payload: Raw user input from request
        
    Returns:
        Tuple of (validated_answers, error_messages)
    """
    errors = []
    
    # Load validation rules from questions.json
    questions_config = load_questions_from_json()
    validation_rules = questions_config.get("validation", {})
    questionnaire = questions_config.get("questionnaire", {})
    
    # Get required fields from configuration
    required_fields = questionnaire.get("required_fields", ["size_m2", "seats"])
    missing_fields = [field for field in required_fields if field not in payload or payload[field] is None]
    
    if missing_fields:
        field_names = {
            "size_m2": "גודל העסק",
            "seats": "מקומות ישיבה"
        }
        missing_names = [field_names.get(f, f) for f in missing_fields]
        errors.append(f"נדרשים שדות: {', '.join(missing_names)}")
    
    # Extract and validate answers
    answers = {
        "size_m2": payload.get("size_m2"),
        "seats": payload.get("seats"),
        "uses_gas": payload.get("uses_gas"),
        "serves_meat": payload.get("serves_meat"),
        "attributes": payload.get("attributes", [])
    }
    
    # Validate numeric ranges using configuration
    if answers["size_m2"] is not None:
        size_rules = validation_rules.get("size_m2", {})
        min_val = size_rules.get("min", 1)
        max_val = size_rules.get("max", 10000)
        error_msg = size_rules.get("error_message", "גודל העסק חייב להיות בין 1 ל-10,000 מ\"ר")
        
        if answers["size_m2"] <= 0 or answers["size_m2"] > max_val:
            errors.append(error_msg)
            
    if answers["seats"] is not None:
        seats_rules = validation_rules.get("seats", {})
        min_val = seats_rules.get("min", 0)
        max_val = seats_rules.get("max", 1000)
        error_msg = seats_rules.get("error_message", "מספר מקומות הישיבה חייב להיות בין 0 ל-1,000")
        
        if answers["seats"] < min_val or answers["seats"] > max_val:
            errors.append(error_msg)
    
    # Clean up None values
    answers = {k: v for k, v in answers.items() if v is not None}
    
    return answers, errors


def assess_business_risk_factors(matching_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Assess business risk factors based on requirements.
    
    Args:
        matching_result: Result from match_requirements()
        
    Returns:
        List of risk factor dictionaries
    """
    risk_factors = []
    
    high_priority_count = matching_result["summary"]["priority_breakdown"]["high"]
    if high_priority_count > 5:
        risk_factors.append({
            "category": "high_regulation_burden",
            "description": f"עסק עם {high_priority_count} דרישות בעדיפות גבוהה",
            "recommendation": "מומלץ להתייעץ עם יועץ רגולטורי"
        })
    
    profile = matching_result["summary"]["business_profile"]
    if profile.get("special_requirements"):
        risk_factors.append({
            "category": "special_requirements",
            "description": "עסק עם דרישות מיוחדות (גז/בשר)",
            "recommendation": "נדרשת התייחסות מיוחדת לדרישות בטיחות"
        })
    
    return risk_factors


def generate_recommendations(matching_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate actionable recommendations based on analysis.
    
    Args:
        matching_result: Result from match_requirements()
        
    Returns:
        Dictionary containing recommendations
    """
    high_priority = [r for r in matching_result["matched_requirements"] if r.get("priority") == "high"]
    
    recommendations = {
        "immediate_actions": [
            f"טפל בדרישות עדיפות גבוהה: {len(high_priority)} דרישות"
        ],
        "categories_to_focus": list(matching_result["by_category"].keys())[:3],
        "estimated_complexity": "medium" if len(matching_result["matched_requirements"]) < 30 else "high"
    }
    
    return recommendations


def create_questionnaire_from_json(feature_options: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create complete questionnaire from questions.json with dynamic feature options.
    
    Args:
        feature_options: List of feature options for multiselect
        
    Returns:
        Tuple of (questions_list, metadata_dict)
    """
    questions_config = load_questions_from_json()
    
    if not questions_config:
        # Fallback to hardcoded questions if JSON loading fails
        return _create_fallback_questions(feature_options)
    
    questionnaire = questions_config.get("questionnaire", {})
    questions = questions_config.get("questions", [])
    
    # Add feature options to the attributes question
    for question in questions:
        if question.get("name") == "attributes":
            question["options"] = feature_options
            break
    
    # Create metadata
    metadata = {
        "questionnaire_version": questionnaire.get("version", "1.1"),
        "required_fields": questionnaire.get("required_fields", ["size_m2", "seats"]),
        "description": questionnaire.get("description", "שאלון רישוי עסקים מסעדות"),
        "instructions": questionnaire.get("instructions", "מלא את השדות הנדרשים"),
        "features_loaded": len(feature_options)
    }
    
    return questions, metadata


def _create_fallback_questions(feature_options: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create fallback questions if JSON loading fails.
    
    Args:
        feature_options: List of feature options for multiselect
        
    Returns:
        Tuple of (questions_list, metadata_dict)
    """
    questions = [
        {
            "name": "size_m2",
            "label": "גודל העסק (מ\"ר)",
            "type": "number",
            "required": True,
            "min": 1,
            "max": 10000,
            "placeholder": "לדוגמה: 150",
            "description": "שטח העסק במטרים מרובעים - נדרש לצורך סינון דרישות"
        },
        {
            "name": "seats",
            "label": "מספר מקומות ישיבה / תפוסה",
            "type": "number",
            "required": True,
            "min": 0,
            "max": 1000,
            "placeholder": "לדוגמה: 50",
            "description": "מספר לקוחות שיכולים לשבת במקום - נדרש לצורך סינון דרישות"
        },
        {
            "name": "attributes",
            "label": "מאפייני עסק נוספים",
            "type": "multiselect",
            "required": False,
            "options": feature_options,
            "description": "בחר את כל המאפיינים הרלוונטיים - מאפיינים נוספים המשפיעים על דרישות הרגולציה"
        }
    ]
    
    metadata = {
        "questionnaire_version": "1.1",
        "required_fields": ["size_m2", "seats"],
        "description": "שאלון רישוי עסקים מסעדות לפי משימה טכנית",
        "instructions": "יש למלא לפחות את השדות הנדרשים (גודל ותפוסה) כדי לקבל ניתוח מדויק",
        "features_loaded": len(feature_options)
    }
    
    return questions, metadata


def create_questionnaire_metadata(feature_options: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Create metadata for the questionnaire response.
    
    Args:
        feature_options: List of feature options for multiselect
        
    Returns:
        Metadata dictionary
    """
    return {
        "questionnaire_version": "1.1",
        "required_fields": ["size_m2", "seats"],
        "description": "שאלון רישוי עסקים מסעדות לפי משימה טכנית",
        "instructions": "יש למלא לפחות את השדות הנדרשים (גודל ותפוסה) כדי לקבל ניתוח מדויק",
        "features_loaded": len(feature_options)
    }


def create_analysis_metadata() -> Dict[str, str]:
    """
    Create metadata for the analysis response.
    
    Returns:
        Metadata dictionary with timestamp and version info
    """
    from datetime import datetime
    
    return {
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "version": "1.0", 
        "algorithm": "משימה_specification_matching",
        "data_source": "hebrew_regulatory_parser"
    }
