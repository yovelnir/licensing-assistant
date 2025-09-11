import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from .rules_loader import get_paragraphs, get_mappings, get_paragraph_text

# ---------- Business Logic Helpers ----------

def _to_float(x: Any) -> Optional[float]:
    """Convert value to float, handling various input types safely."""
    try:
        return float(x) if x is not None else None
    except (TypeError, ValueError):
        return None

def _normalize_user_input(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize user input for consistent processing.
    
    Supports multiple input formats:
    - size_m2: Business floor area in square meters
    - seats/seating: Number of seats/occupancy
    - uses_gas: Boolean or in attributes list
    - serves_meat: Boolean or in attributes list
    - attributes: List of business characteristics
    """
    size = _to_float(answers.get("size_m2"))
    seats = _to_float(answers.get("seats"))
    if seats is None:
        seats = _to_float(answers.get("seating"))

    attrs = list(str(attr).lower() for attr in (answers.get("attributes") or []))
    
    # Extract boolean flags from various sources
    uses_gas = answers.get("uses_gas")
    if uses_gas is None:
        uses_gas = any(gas_term in attrs for gas_term in ["uses_gas", "gas", "גז"])

    serves_meat = answers.get("serves_meat")
    if serves_meat is None:
        serves_meat = any(meat_term in attrs for meat_term in ["serves_meat", "meat", "בשר"])
    
    # Check for gas usage in attributes (from features.json)
    if not uses_gas:
        uses_gas = "גז" in attrs

    return {
        "size_m2": size,
        "seats": seats,
        "attributes": list(attrs),  # Ensure it's a list for JSON serialization
        "uses_gas": bool(uses_gas) if uses_gas is not None else False,
        "serves_meat": bool(serves_meat) if serves_meat is not None else False,
    }

def _extract_numeric_ranges(text: str) -> dict:
    """
    Extract numeric ranges and thresholds from Hebrew regulatory text.
    
    Returns structured information about size and occupancy requirements.
    """
    if not text:
        return {}
    
    ranges = {
        'size_m2': {'min': None, 'max': None, 'exact': []},
        'occupancy': {'min': None, 'max': None, 'exact': []}
    }
    
    
    # Hebrew patterns for size (מ"ר, מטר מרובע)
    # Using named groups to identify constraint types
    size_patterns = [
        # Exact ranges: "100-200 מ"ר", "בין 50 ל-100 מ"ר"
        (r'בין\s+(\d+)\s+ל[־\-]?(\d+)\s*(?:מ["\u05f4׳]?ר|מטר)', 'range'),
        (r'(\d+)[־\-–—](\d+)\s*(?:מ["\u05f4׳]?ר|מטר)', 'range'),
        
        # Minimum thresholds: "מעל 100 מ"ר", "יותר מ-50 מ"ר", "לפחות 200 מ"ר"
        (r'(?:מעל|יותר\s*מ[־\-]?|לפחות|החל\s*מ[־\-]?)\s*(\d+)\s*(?:מ["\u05f4׳]?ר|מטר)', 'min'),
        
        # Maximum thresholds: "עד 100 מ"ר", "לא יעלה על 150 מ"ר", "פחות מ-80 מ"ר"  
        (r'(?:עד|לא\s*יעלה\s*על|פחות\s*מ[־\-]?|לא\s*יותר\s*מ[־\-]?)\s*(\d+)\s*(?:מ["\u05f4׳]?ר|מטר)', 'max'),
        
        # Exact values: "120 מ"ר", "גודלו 200 מ"ר" (only if no other constraint words)
        (r'(?:^|[^א-ת])(\d+)\s*(?:מ["\u05f4׳]?ר|מטר)(?![א-ת])', 'exact'),
    ]
    
    # Hebrew patterns for occupancy (איש, מקומות, תפוסה)
    # Using named groups to identify constraint types
    occupancy_patterns = [
        # Exact ranges: "30-50 איש", "בין 20 ל-40 מקומות"
        (r'בין\s+(\d+)\s+ל[־\-]?(\d+)\s*(?:איש|אנשים|מקומות?)', 'range'),
        (r'(\d+)[־\-–—](\d+)\s*(?:איש|אנשים|מקומות?)', 'range'),
        
        # Minimum thresholds: "מעל 30 איש", "יותר מ-50 מקומות"
        (r'(?:מעל|יותר\s*מ[־\-]?|לפחות|החל\s*מ[־\-]?)\s*(\d+)\s*(?:איש|אנשים|מקומות?)', 'min'),
        
        # Maximum thresholds: "עד 100 איש", "לא יותר מ-50 מקומות"
        (r'(?:עד|לא\s*יעלה\s*על|פחות\s*מ[־\-]?|לא\s*יותר\s*מ[־\-]?)\s*(\d+)\s*(?:איש|אנשים|מקומות?)', 'max'),
        
        # Exact values: "50 איש", "תפוסה של 100 מקומות" (context-dependent)
        (r'(?:תפוסה\s*של\s*|מיועד\s*ל[־\-]?)\s*(\d+)\s*(?:איש|אנשים|מקומות?)', 'exact'),
    ]
    
    # Extract size ranges with constraint type awareness
    for pattern, constraint_type in size_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.UNICODE)
        for match in matches:
            try:
                if constraint_type == 'range' and isinstance(match, tuple) and len(match) == 2:
                    min_val, max_val = float(match[0]), float(match[1])
                    ranges['size_m2']['min'] = min_val
                    ranges['size_m2']['max'] = max_val
                elif constraint_type == 'min':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['size_m2']['min'] = val
                elif constraint_type == 'max':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['size_m2']['max'] = val
                elif constraint_type == 'exact':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['size_m2']['exact'].append(val)
            except (ValueError, TypeError):
                continue
    
    # Extract occupancy ranges with constraint type awareness
    for pattern, constraint_type in occupancy_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.UNICODE)
        for match in matches:
            try:
                if constraint_type == 'range' and isinstance(match, tuple) and len(match) == 2:
                    min_val, max_val = float(match[0]), float(match[1])
                    ranges['occupancy']['min'] = min_val
                    ranges['occupancy']['max'] = max_val
                elif constraint_type == 'min':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['occupancy']['min'] = val
                elif constraint_type == 'max':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['occupancy']['max'] = val
                elif constraint_type == 'exact':
                    val = float(match if isinstance(match, str) else match[0])
                    ranges['occupancy']['exact'].append(val)
            except (ValueError, TypeError):
                continue
    
    # Clean up exact values (remove duplicates, sort)
    ranges['size_m2']['exact'] = sorted(list(set(ranges['size_m2']['exact'])))
    ranges['occupancy']['exact'] = sorted(list(set(ranges['occupancy']['exact'])))
    
    return ranges


def _matches_numeric_requirements(user_profile: Dict[str, Any], paragraph_ranges: dict) -> bool:
    """
    Check if user's business characteristics match the numeric requirements in paragraph.
    
    Args:
        user_profile: User's normalized business profile
        paragraph_ranges: Extracted numeric ranges from paragraph text
        
    Returns:
        True if user meets the numeric requirements, False otherwise
    """
    user_size = user_profile.get("size_m2") or 0
    user_seats = user_profile.get("seats") or 0
    
    # Check size requirements
    size_reqs = paragraph_ranges.get('size_m2', {})
    if size_reqs.get('min') is not None and user_size < size_reqs['min']:
        return False
    if size_reqs.get('max') is not None and user_size > size_reqs['max']:
        return False
    
    # Check occupancy requirements  
    occupancy_reqs = paragraph_ranges.get('occupancy', {})
    if occupancy_reqs.get('min') is not None and user_seats < occupancy_reqs['min']:
        return False
    if occupancy_reqs.get('max') is not None and user_seats > occupancy_reqs['max']:
        return False
    
    # If paragraph has specific size/occupancy requirements but user doesn't match any
    has_size_reqs = size_reqs.get('min') or size_reqs.get('max') or size_reqs.get('exact')
    has_occupancy_reqs = occupancy_reqs.get('min') or occupancy_reqs.get('max') or occupancy_reqs.get('exact')
    
    if has_size_reqs and user_size == 0:
        return False  # Can't match size requirements without size info
    if has_occupancy_reqs and user_seats == 0:
        return False  # Can't match occupancy requirements without occupancy info
    
    return True



# ---------- Feature-Based Matching ----------

def _load_features_from_json():
    """Load features from features.json file for dynamic matching."""
    try:
        features_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "features.json"
        with features_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load features.json: {e}")
        return {}

def _matches_user_profile(user_profile: Dict[str, Any], feature: str) -> bool:
    """
    Determine if a feature applies to the user's business profile.
    
    Uses dynamic feature loading from features.json and business logic:
    - Size-related features: מ\"ר (square meters) - always apply
    - Occupancy features: תפוסה (occupancy/seating) - always apply
    - Dynamic features from features.json - only if selected by user
    - Safety features: בטיחות (safety) - always apply
    
    Args:
        user_profile: Normalized user input
        feature: Feature name from mappings.json
        
    Returns:
        True if feature applies to this user's business
    """
    size = user_profile.get("size_m2") or 0
    seats = user_profile.get("seats") or 0
    attributes = user_profile.get("attributes", [])
    
    # Load dynamic features from features.json
    features_data = _load_features_from_json()
    dynamic_features = list(features_data.keys())
    
    # Feature matching logic using Specification pattern
    feature_lower = feature.lower()
    
    # Size-related features - apply to all businesses
    if "מ\"ר" in feature or "size" in feature_lower or "שטח" in feature:
        return True
        
    # Occupancy/seating features - apply to all restaurants  
    if "תפוסה" in feature or "seats" in feature_lower or "איש" in feature:
        return True
        
    # Dynamic features from features.json - only if user selected them
    for dynamic_feature in dynamic_features:
        if dynamic_feature in feature:
            # Skip size and occupancy as they are always applied
            if dynamic_feature in ["מ\"ר", "תפוסה"]:
                continue
            # For other dynamic features, check if user selected them
            return dynamic_feature in attributes
        
    # Safety features - apply to all businesses (general safety requirements)
    if any(safety_term in feature for safety_term in ["בטיחות", "safety", "כיבוי", "fire"]):
        return True
        
    # Default: apply feature unless explicitly excluded
    return True

def _assess_requirement_relevance(paragraph_text: str, user_profile: Dict[str, Any], paragraph_ranges: dict = None) -> float:
    """
    Assess how relevant a requirement paragraph is to the user's business.
    
    Uses content analysis and numeric range matching to score relevance.
    Now includes precise range-based matching for size and occupancy requirements.
    
    Args:
        paragraph_text: Text content of the regulation paragraph
        user_profile: User's business characteristics
        paragraph_ranges: Pre-extracted numeric ranges (optional, will extract if None)
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    if not paragraph_text:
        return 0.0
    
    # Extract ranges if not provided
    if paragraph_ranges is None:
        paragraph_ranges = _extract_numeric_ranges(paragraph_text)
        
    text_lower = paragraph_text.lower()
    user_size = user_profile.get("size_m2") or 0
    user_seats = user_profile.get("seats") or 0
    
    # Base relevance starts lower, will be boosted by specific matches
    relevance_score = 0.3
    
    # Range-based relevance scoring (most important factor)
    size_reqs = paragraph_ranges.get('size_m2', {})
    occupancy_reqs = paragraph_ranges.get('occupancy', {})
    
    # Size-based relevance with precise range matching
    if user_size > 0 and (size_reqs.get('min') or size_reqs.get('max') or size_reqs.get('exact')):
        size_match_score = 0.0
        
        # Check if user size fits within specified ranges
        if size_reqs.get('min') and user_size >= size_reqs['min']:
            size_match_score += 0.4
        if size_reqs.get('max') and user_size <= size_reqs['max']:
            size_match_score += 0.4
            
        # Check exact values proximity
        for exact_val in size_reqs.get('exact', []):
            if abs(user_size - exact_val) <= user_size * 0.3:  # Within 30% range
                size_match_score += 0.3
                break
                
        relevance_score += min(size_match_score, 0.4)
    
    # Occupancy-based relevance with precise range matching
    if user_seats > 0 and (occupancy_reqs.get('min') or occupancy_reqs.get('max') or occupancy_reqs.get('exact')):
        occupancy_match_score = 0.0
        
        # Check if user occupancy fits within specified ranges
        if occupancy_reqs.get('min') and user_seats >= occupancy_reqs['min']:
            occupancy_match_score += 0.4
        if occupancy_reqs.get('max') and user_seats <= occupancy_reqs['max']:
            occupancy_match_score += 0.4
            
        # Check exact values proximity
        for exact_val in occupancy_reqs.get('exact', []):
            if abs(user_seats - exact_val) <= user_seats * 0.3:  # Within 30% range
                occupancy_match_score += 0.3
                break
                
        relevance_score += min(occupancy_match_score, 0.4)
    
    # Dynamic feature-specific relevance - only if user selected the features
    attributes = user_profile.get("attributes", [])
    features_data = _load_features_from_json()
    
    # Check each dynamic feature from features.json
    for feature_key, feature_data in features_data.items():
        if feature_key in attributes:
            # Check if this feature is mentioned in the paragraph text
            keywords = feature_data.get("keywords", [])
            if isinstance(keywords, list):
                for keyword in keywords:
                    if isinstance(keyword, str) and keyword in paragraph_text:
                        relevance_score += 0.2
                        break
                    elif isinstance(keyword, dict) and keyword.get("regex"):
                        import re
                        if re.search(keyword["pattern"], paragraph_text, re.IGNORECASE | re.UNICODE):
                            relevance_score += 0.2
                            break
    
    # Meat-serving specific relevance (legacy)
    if user_profile.get("serves_meat") and ("בשר" in paragraph_text or "meat" in text_lower or "כשר" in paragraph_text):
        relevance_score += 0.1
        
    # High-priority safety terms (always boost relevance)
    high_priority_terms = ["חירום", "בטיחות", "כיבוי", "emergency", "safety", "fire", "מתזים", "גלאי"]
    if any(term in text_lower for term in high_priority_terms):
        relevance_score += 0.3
    
    # Penalty for requirements that clearly don't match user's business size/occupancy
    if not _matches_numeric_requirements(user_profile, paragraph_ranges):
        relevance_score *= 0.2  # Significant penalty for non-matching requirements
    
    return min(relevance_score, 1.0)

# ---------- Public API ----------

def get_applicable_features(user_answers: Dict[str, Any]) -> List[str]:
    """
    Identify which regulatory features apply to the user's business.
    
    Based on משימה.md requirements:
    - Filter by business size (גודל העסק)
    - Filter by seating/occupancy (מקומות ישיבה/תפוסה)  
    - Consider special characteristics (מאפיינים מיוחדים)
    
    Args:
        user_answers: User's business characteristics
        
    Returns:
        List of applicable feature names
    """
    user_profile = _normalize_user_input(user_answers)
    mappings = get_mappings()
    
    applicable_features = []
    for feature_name in mappings.keys():
        if _matches_user_profile(user_profile, feature_name):
            applicable_features.append(feature_name)
    
    # Sort for consistent ordering
    return sorted(applicable_features)

def match_requirements(user_answers: Dict[str, Any], min_relevance: float = 0.3) -> Dict[str, Any]:
    """
    Match user business characteristics to applicable regulatory requirements.
    
    Implements משימה.md requirements:
    - סינון לפי גודל ותפוסה (Filter by size and occupancy)
    - התחשבות במאפיינים מיוחדים (Consider special characteristics)
    - יצירת דוח מותאם (Create customized report)
    
    Uses Repository pattern for data access and Specification pattern
    for complex business rule evaluation.
    
    Args:
        user_answers: User's business characteristics and attributes
        min_relevance: Minimum relevance threshold (0.0 to 1.0)
        
    Returns:
        Dictionary containing:
        - matched_requirements: List of applicable regulation paragraphs
        - by_category: Requirements grouped by regulatory category
        - feature_coverage: Which features were matched
        - user_profile: Normalized user profile used for matching
        - summary: Summary statistics for reporting
    """
    user_profile = _normalize_user_input(user_answers)
    paragraphs = get_paragraphs()
    mappings = get_mappings()
    
    # Get applicable features
    applicable_features = get_applicable_features(user_answers)
    
    # Collect matching paragraphs
    matched_paragraphs = []
    by_category = {}
    
    for feature_name in applicable_features:
        if feature_name not in mappings:
            continue
            
        feature_mapping = mappings[feature_name]
        categories = feature_mapping.get("categories", {})
        
        for category, paragraph_numbers in categories.items():
            if category not in by_category:
                by_category[category] = []
                
            for paragraph_num in paragraph_numbers:
                # Get paragraph text
                text = get_paragraph_text(paragraphs, category, paragraph_num)
                if not text:
                    continue
                
                # Extract numeric ranges from paragraph
                paragraph_ranges = _extract_numeric_ranges(text)
                
                # First check if user matches the numeric requirements
                if not _matches_numeric_requirements(user_profile, paragraph_ranges):
                    # Skip requirements that don't match user's size/occupancy constraints
                    continue
                
                # Assess relevance with range information
                relevance = _assess_requirement_relevance(text, user_profile, paragraph_ranges)
                if relevance < min_relevance:
                    continue
                
                requirement = {
                    "category": category,
                    "paragraph_number": paragraph_num,
                    "text": text,
                    "relevance_score": relevance,
                    "matched_features": [feature_name],
                    "source": "feature_mapping",
                    "numeric_ranges": paragraph_ranges
                }
                
                matched_paragraphs.append(requirement)
                by_category[category].append(requirement)
    
    # Sort by relevance score (descending)
    matched_paragraphs.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Sort within categories
    for category in by_category:
        by_category[category].sort(key=lambda x: (x["relevance_score"], x["paragraph_number"]), reverse=True)
    
    # Calculate summary statistics and assign priorities
    priority_counts = {"high": 0, "medium": 0, "low": 0}
    for req in matched_paragraphs:
        # Assign priority based on relevance score and safety keywords
        text_lower = req["text"].lower()
        if (req["relevance_score"] >= 0.8 or 
            any(term in text_lower for term in ["חירום", "בטיחות", "כיבוי", "emergency", "safety"])):
            req["priority"] = "high"
            priority_counts["high"] += 1
        elif req["relevance_score"] >= 0.5:
            req["priority"] = "medium"
            priority_counts["medium"] += 1 
        else:
            req["priority"] = "low"
            priority_counts["low"] += 1
    
    return {
        "matched_requirements": matched_paragraphs,
        "by_category": by_category, 
        "feature_coverage": applicable_features,  # Already a list now
        "user_profile": user_profile,
        "total_matches": len(matched_paragraphs),
        "summary": {
            "categories_count": len(by_category),
            "priority_breakdown": priority_counts,
            "avg_relevance": sum(r["relevance_score"] for r in matched_paragraphs) / len(matched_paragraphs) if matched_paragraphs else 0,
            "business_profile": {
                "size_category": "small" if user_profile.get("size_m2", 0) < 100 else "large",
                "occupancy_category": "low" if user_profile.get("seats", 0) < 50 else "high",
                "special_requirements": user_profile.get("uses_gas", False) or user_profile.get("serves_meat", False)
            }
        }
    }
