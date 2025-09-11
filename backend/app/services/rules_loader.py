import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Tuple


@lru_cache(maxsize=1)
def load_parser_data() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load processed parser outputs for regulatory requirements matching.
    
    Uses the Singleton pattern with LRU cache for efficient memory usage.
    
    Returns:
        Tuple of (paragraphs, mappings) where:
        - paragraphs: Hierarchical document structure by category
        - mappings: Feature-to-paragraph mappings for content classification
    """
    base = Path(__file__).resolve().parents[1]
    
    # Load hierarchical document structure
    paragraphs_path = base / "data" / "processed" / "paragraphs.json"
    with paragraphs_path.open("r", encoding="utf-8") as f:
        paragraphs = json.load(f)
    
    # Load feature mappings
    mappings_path = base / "data" / "processed" / "mappings.json"
    with mappings_path.open("r", encoding="utf-8") as f:
        mappings = json.load(f)
    
    return paragraphs, mappings


def get_paragraphs() -> Dict[str, Any]:
    """Get hierarchical paragraph structure."""
    paragraphs, _ = load_parser_data()
    return paragraphs


def get_mappings() -> Dict[str, Any]:
    """Get feature mappings."""
    _, mappings = load_parser_data()
    return mappings


def get_paragraph_text(paragraphs: Dict[str, Any], category: str, number: str) -> str:
    """
    Extract text content from a specific paragraph.
    
    Args:
        paragraphs: Hierarchical paragraph structure
        category: Document category (e.g., 'הרשות הארצית לכבאות והצלה')
        number: Paragraph number (e.g., '5.1.1')
        
    Returns:
        Paragraph text content or empty string if not found
    """
    if category not in paragraphs:
        return ""
    
    current = paragraphs[category]
    
    # Navigate through hierarchical structure
    parts = number.split(".")
    for i, part in enumerate(parts):
        current_key = ".".join(parts[:i+1])
        if current_key not in current:
            return ""
        current = current[current_key]
        
        if not isinstance(current, dict):
            return str(current) if current else ""
    
    return current.get("text", "") if isinstance(current, dict) else str(current)
