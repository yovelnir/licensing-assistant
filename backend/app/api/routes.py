from flask import Blueprint, jsonify, request
from app.services.matching import match_requirements, get_applicable_features
from app.services.rules_loader import get_mappings
from app.api.helpers import (
    load_features_from_json,
    create_feature_question_options,
    create_questionnaire_from_json,
    validate_user_input,
    assess_business_risk_factors,
    generate_recommendations,
    create_analysis_metadata
)

api_blueprint = Blueprint("api", __name__)


@api_blueprint.get("/")
def index():
    return jsonify({"message": "A-Impact Licensing Assistant API"})


@api_blueprint.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@api_blueprint.get("/features")
def get_features():
    """Get available regulatory features for debugging/information."""
    try:
        mappings = get_mappings()
        return jsonify({
            "features": list(mappings.keys()),
            "total_features": len(mappings),
            "feature_details": {
                name: {
                    "categories": list(mapping.get("categories", {}).keys()),
                    "paragraph_count": len(mapping.get("paragraphs", []))
                }
                for name, mapping in mappings.items()
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@api_blueprint.get("/questions")
def get_questions():
    """
    Digital questionnaire per משימה.md requirements.
    
    Collects required information:
    - גודל העסק (במ"ר) - Business size in square meters
    - מספר מקומות ישיבה/תפוסה - Number of seats/occupancy  
    - מאפיין אחד נוסף לפחות - At least one additional characteristic
    
    Uses the Repository pattern for consistent data access.
    Questions are loaded from questions.json for better maintainability.
    """
    # Load features from features.json
    features_data = load_features_from_json()
    feature_options = create_feature_question_options(features_data)
    
    # Create questionnaire from JSON configuration
    questions, metadata = create_questionnaire_from_json(feature_options)
    
    return jsonify({
        "questions": questions,
        "metadata": metadata
    })


@api_blueprint.post("/analyze")
def analyze():
    """
    Analyze business profile per משימה.md requirements.
    
    Implements:
    - סינון לפי גודל ותפוסה (Filtering by size and occupancy)
    - התחשבות במאפיינים מיוחדים (Consider special characteristics)
    - יצירת דוח מותאם אישית (Generate personalized report)
    
    Returns structured requirements grouped by regulatory category.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Validate user input using helper function
        answers, validation_errors = validate_user_input(payload)
        
        if validation_errors:
            return jsonify({
                "error": "Validation error",
                "message": "; ".join(validation_errors)
            }), 400
        
        # Execute matching logic per משימה.md requirements
        matching_result = match_requirements(answers, min_relevance=0.2)
        
        # Format response with business intelligence
        response = {
            "user_input": answers,
            "business_analysis": {
                "profile": matching_result["user_profile"],
                "classification": matching_result["summary"]["business_profile"],
                "risk_factors": assess_business_risk_factors(matching_result)
            },
            "regulatory_analysis": {
                "matched_requirements": matching_result["matched_requirements"],
                "by_category": matching_result["by_category"],
                "total_matches": matching_result["total_matches"],
                "priority_breakdown": matching_result["summary"]["priority_breakdown"],
                "avg_relevance": matching_result["summary"]["avg_relevance"]
            },
            "feature_coverage": matching_result["feature_coverage"],
            "recommendations": generate_recommendations(matching_result),
            "analysis_metadata": create_analysis_metadata()
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({
            "error": "Validation error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "שגיאה בניתוח הדרישות הרגולטוריות"
        }), 500




@api_blueprint.post("/preview-features")
def preview_features():
    """
    Preview which features would apply to user input without full analysis.
    
    Useful for progressive disclosure and user guidance.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Get applicable features
        applicable_features = get_applicable_features(payload)
        
        return jsonify({
            "applicable_features": list(applicable_features),
            "total_features": len(applicable_features),
            "user_input": payload
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred during feature preview"
        }), 500
