from flask import Blueprint, jsonify, request
import logging

# Configure logging
logger = logging.getLogger(__name__)
from app.services.matching import match_requirements, get_applicable_features
from app.services.rules_loader import get_mappings
from app.services.ai_service import generate_ai_report, ai_service
from app.api.helpers import (
    load_features_from_json,
    load_questions_from_json,
    create_feature_question_options,
    create_questionnaire_from_json,
    validate_user_input,
    assess_business_risk_factors,
    generate_recommendations,
    create_analysis_metadata
)

api_blueprint = Blueprint("api", __name__)


def _prepare_business_data(answers, matching_result):
    """Helper function to prepare business data for AI processing."""
    return {
        "size_m2": answers.get("size_m2", 0),
        "seats": answers.get("seats", 0),
        "attributes": answers.get("attributes", []),
        "matched_requirements": matching_result["matched_requirements"],
        "by_category": matching_result["by_category"],
        "feature_coverage": matching_result["feature_coverage"],
        "summary": matching_result["summary"]
    }


def _prepare_business_analysis(matching_result):
    """Helper function to prepare business analysis data."""
    return {
        "profile": matching_result.get("user_profile", {}),
        "classification": matching_result["summary"].get("business_profile", {}),
        "risk_factors": assess_business_risk_factors(matching_result)
    }


def _prepare_regulatory_analysis(matching_result):
    """Helper function to prepare regulatory analysis data."""
    return {
        "matched_requirements": matching_result["matched_requirements"],
        "by_category": matching_result["by_category"],
        "total_matches": matching_result["total_matches"],
        "priority_breakdown": matching_result["summary"]["priority_breakdown"],
        "avg_relevance": matching_result["summary"]["avg_relevance"]
    }


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
            "business_analysis": _prepare_business_analysis(matching_result),
            "regulatory_analysis": _prepare_regulatory_analysis(matching_result),
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


@api_blueprint.post("/generate-ai-report")
def generate_ai_report_endpoint():
    """
    Generate AI-powered smart report per משימה.md requirements.
    
    This is the central AI integration endpoint that:
    - עיבוד חכם של הדרישות (Smart processing of requirements)
    - התאמה אישית (Personalized adaptation)
    - שפה ברורה ונגישה (Clear and accessible language)
    - ארגון תוכן (Content organization)
    
    Uses the Strategy pattern for AI provider selection and fallback.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Validate user input
        answers, validation_errors = validate_user_input(payload)
        
        if validation_errors:
            return jsonify({
                "error": "Validation error",
                "message": "; ".join(validation_errors)
            }), 400
        
        # Get report type from request (default: comprehensive)
        report_type = payload.get("report_type", "comprehensive")
        if report_type not in ["comprehensive", "checklist"]:
            report_type = "comprehensive"
        
        # Execute matching logic to get regulatory analysis
        matching_result = match_requirements(answers, min_relevance=0.2)
        
        # Prepare business data for AI processing
        business_data = _prepare_business_data(answers, matching_result)
        business_analysis = _prepare_business_analysis(matching_result)
        
        recommendations = generate_recommendations(matching_result)
        
        # Generate AI report using OpenAI
        try:
            ai_response = generate_ai_report(business_data, report_type)
        except Exception as e:
            logger.error(f"Exception during AI report generation: {e}")
            return jsonify({
                "error": "AI report generation failed",
                "message": f"שגיאה ביצירת דוח AI: {str(e)}"
            }), 500
        
        if not ai_response.success:
            logger.error(f"AI report generation failed: {ai_response.error_message}")
            return jsonify({
                "error": "AI report generation failed",
                "message": ai_response.error_message or "Unable to generate AI report. Please check your OpenAI API key."
            }), 500
        
        # Prepare response with AI-generated content
        response = {
            "ai_report": {
                "content": ai_response.content,
                "provider": ai_response.provider.value,
                "model_used": ai_response.model_used,
                "tokens_used": ai_response.tokens_used,
                "success": ai_response.success,
                "error_message": ai_response.error_message,
                "generation_timestamp": matching_result.get("analysis_metadata", {}).get("timestamp")
            },
            "business_analysis": business_analysis,
            "regulatory_analysis": _prepare_regulatory_analysis(matching_result),
            "feature_coverage": matching_result["feature_coverage"],
            "recommendations": recommendations,
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
            "message": "שגיאה ביצירת דוח AI"
        }), 500


@api_blueprint.get("/ai-providers")
def get_ai_providers():
    """
    Get information about available AI providers.
    
    Useful for debugging and monitoring AI service availability.
    """
    try:
        available_providers = ai_service.get_available_providers()
        
        provider_info = {}
        for provider in ai_service.provider_order:
            strategy = ai_service.strategies[provider]
            provider_info[provider.value] = {
                "available": strategy.is_available(),
                "name": provider.value.title(),
                "description": _get_provider_description(provider)
            }
        
        return jsonify({
            "available_providers": [p.value for p in available_providers],
            "provider_details": provider_info,
            "total_providers": len(ai_service.provider_order)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "שגיאה בקבלת מידע על ספקי AI"
        }), 500


@api_blueprint.post("/analyze-with-ai")
def analyze_with_ai():
    """
    Combined endpoint: regulatory analysis + AI report generation.
    
    This endpoint combines the existing /analyze functionality with AI report generation
    for a complete solution per משימה.md requirements.
    """
    try:
        payload = request.get_json(silent=True) or {}
        
        # Validate user input
        answers, validation_errors = validate_user_input(payload)
        
        if validation_errors:
            return jsonify({
                "error": "Validation error",
                "message": "; ".join(validation_errors)
            }), 400
        
        # Execute matching logic
        matching_result = match_requirements(answers, min_relevance=0.2)
        
        # Prepare business data and generate AI report
        business_data = _prepare_business_data(answers, matching_result)
        ai_response = generate_ai_report(business_data, "comprehensive")
        
        # Prepare comprehensive response
        response = {
            "user_input": answers,
            "business_analysis": _prepare_business_analysis(matching_result),
            "regulatory_analysis": _prepare_regulatory_analysis(matching_result),
            "feature_coverage": matching_result["feature_coverage"],
            "recommendations": generate_recommendations(matching_result),
            "ai_report": {
                "content": ai_response.content if ai_response.success else "לא ניתן ליצור דוח AI - אנא בדוק את מפתח ה-API",
                "provider": ai_response.provider.value,
                "model_used": ai_response.model_used,
                "tokens_used": ai_response.tokens_used,
                "success": ai_response.success,
                "error_message": ai_response.error_message
            },
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
            "message": "שגיאה בניתוח עם AI"
        }), 500


def _get_provider_description(provider):
    """Get human-readable description for AI provider."""
    descriptions = {
        "openai": "OpenAI GPT - מודל שפה מתקדם עם תמיכה בעברית"
    }
    return descriptions.get(provider.value, "ספק AI לא ידוע")
