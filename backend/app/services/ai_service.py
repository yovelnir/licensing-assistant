"""
AI Service Module for Smart Report Generation

This module implements the Strategy pattern for AI-powered report generation.
Supports multiple AI providers (OpenAI, Claude) with fallback mechanisms.

Per משימה.md requirements:
- אינטגרציה עם מודל שפה (LLM Integration)
- עיבוד חכם של הדרישות (Smart processing of requirements)
- התאמה אישית (Personalized adaptation)
- שפה ברורה ונגישה (Clear and accessible language)
- ארגון תוכן (Content organization)
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"


@dataclass
class AIResponse:
    """Structured response from AI service."""
    content: str
    provider: AIProvider
    success: bool
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class AIProviderStrategy(ABC):
    """Abstract base class for AI provider strategies."""
    
    @abstractmethod
    def generate_report(self, prompt: str, business_data: Dict[str, Any]) -> AIResponse:
        """Generate a smart report using the AI provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass


class OpenAIStrategy(AIProviderStrategy):
    """OpenAI GPT integration strategy."""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4.1-mini"  # Cost-effective model
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                # Initialize with proper configuration for current OpenAI version
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OPENAI_API_KEY not found in environment")
        except ImportError:
            logger.error("OpenAI package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None
    
    def generate_report(self, prompt: str, business_data: Dict[str, Any]) -> AIResponse:
        """Generate report using OpenAI GPT."""
        if not self.is_available():
            return AIResponse(
                content="",
                provider=AIProvider.OPENAI,
                success=False,
                error_message="OpenAI client not available"
            )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "אתה מומחה ברישוי עסקים בישראל. אתה עוזר לבעלי עסקים להבין דרישות רגולטוריות בצורה ברורה ונגישה. תמיד כתוב בעברית."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.5,
                top_p=0.9
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            return AIResponse(
                content=content,
                provider=AIProvider.OPENAI,
                success=True,
                tokens_used=tokens_used,
                model_used=self.model
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.OPENAI,
                success=False,
                error_message=str(e)
            )




class AIService:
    """
    Main AI service class using OpenAI only.
    
    Simplified service with OpenAI integration and error handling.
    """
    
    def __init__(self):
        self.strategies = {
            AIProvider.OPENAI: OpenAIStrategy()
        }
        self.provider_order = [AIProvider.OPENAI]
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available AI providers."""
        return [provider for provider in self.provider_order if self.strategies[provider].is_available()]
    
    def generate_smart_report(self, business_data: Dict[str, Any], report_type: str = "comprehensive") -> AIResponse:
        """
        Generate a smart, personalized report using OpenAI.
        
        Args:
            business_data: Business profile and matched requirements
            report_type: Type of report ("comprehensive" or "checklist")
            
        Returns:
            AIResponse with generated report content
        """
        # Create AI prompt from business data
        prompt = self._create_report_prompt(business_data, report_type)
        
        # Use OpenAI provider
        openai_strategy = self.strategies[AIProvider.OPENAI]
        
        if not openai_strategy.is_available():
            logger.error("OpenAI strategy not available")
            return AIResponse(
                content="",
                provider=AIProvider.OPENAI,
                success=False,
                error_message="OpenAI service not available. Please check your API key."
            )
        
        logger.info(f"Using OpenAI for {report_type} report generation")
        response = openai_strategy.generate_report(prompt, business_data)
        
        if not response.success:
            logger.error(f"OpenAI failed: {response.error_message}")
        
        return response
    
    def _create_report_prompt(self, business_data: Dict[str, Any], report_type: str = "comprehensive") -> str:
        """
        Create a comprehensive prompt for AI report generation.
        
        Per משימה.md requirements:
        - עיבוד חכם של הדרישות (Smart processing of requirements)
        - התאמה אישית (Personalized adaptation)
        - שפה ברורה ונגישה (Clear and accessible language)
        - ארגון תוכן (Content organization)
        """
        # Extract business profile - unified schema with fields at root
        size = business_data.get("size_m2", 0)
        seats = business_data.get("seats", 0)
        attributes = business_data.get("attributes", [])
        summary = business_data.get("summary", {})
        
        # Extract requirements
        requirements = business_data.get("matched_requirements", [])
        by_category = business_data.get("by_category", {})
        feature_coverage = business_data.get("feature_coverage", [])
        
        # Create structured prompt with enhanced context
        prompt_parts = [
            "אתה מומחה ברישוי עסקים בישראל. אני צריך שתכין דוח מפורט ומותאם אישית לבעל עסק.",
            "",
            "## פרטי העסק:",
            f"גודל העסק: {size} מ\"ר",
            f"מספר מקומות ישיבה: {seats}",
            f"מאפיינים נוספים: {', '.join(attributes) if attributes else 'אין'}",
            f"סיווג עסק: {summary.get('business_profile', {}).get('size_category', 'לא ידוע')} (גודל), {summary.get('business_profile', {}).get('occupancy_category', 'לא ידוע')} (תפוסה)",
            f"דרישות מיוחדות: {'כן' if summary.get('business_profile', {}).get('special_requirements', False) else 'לא'}",
            "",
            "## ניתוח דרישות רגולטוריות:",
            f"סה\"כ דרישות רלוונטיות: {len(requirements)}",
            f"קטגוריות רגולטוריות: {len(by_category)}",
            f"ממוצע רלוונטיות: {summary.get('avg_relevance', 0):.2f}",
            f"כיסוי מאפיינים: {', '.join(feature_coverage)}",
            "",
            "## דרישות רגולטוריות מפורטות:",
        ]
        
        # Add requirements by category with enhanced details
        for category, reqs in by_category.items():
            if reqs:
                prompt_parts.append(f"\n### {category}:")
                prompt_parts.append(f"מספר דרישות: {len(reqs)}")
                
                for i, req in enumerate(reqs[:8]):  # Increased from 5 to 8 per category
                    priority = req.get("priority", "medium")
                    relevance = req.get("relevance_score", 0)
                    text = req.get("text", "")
                    paragraph_num = req.get("paragraph_number", "")
                    matched_features = req.get("matched_features", [])
                    numeric_ranges = req.get("numeric_ranges", {})
                    
                    # Include full text instead of truncating
                    prompt_parts.append(f"\n#### דרישה {i+1} - סעיף {paragraph_num} [{priority.upper()}] (רלוונטיות: {relevance:.2f})")
                    prompt_parts.append(f"מאפיינים מותאמים: {', '.join(matched_features)}")
                    
                    # Add numeric constraints if available
                    if numeric_ranges:
                        size_reqs = numeric_ranges.get('size_m2', {})
                        occupancy_reqs = numeric_ranges.get('occupancy', {})
                        constraints = []
                        if size_reqs.get('min'):
                            constraints.append(f"גודל מינימלי: {size_reqs['min']} מ\"ר")
                        if size_reqs.get('max'):
                            constraints.append(f"גודל מקסימלי: {size_reqs['max']} מ\"ר")
                        if occupancy_reqs.get('min'):
                            constraints.append(f"תפוסה מינימלית: {occupancy_reqs['min']} איש")
                        if occupancy_reqs.get('max'):
                            constraints.append(f"תפוסה מקסימלית: {occupancy_reqs['max']} איש")
                        if constraints:
                            prompt_parts.append(f"אילוצים מספריים: {', '.join(constraints)}")
                    
                    # Include full text (not truncated)
                    prompt_parts.append(f"תוכן הדרישה:")
                    prompt_parts.append(f"{text}")
                    prompt_parts.append("---")
        
        # Add priority breakdown
        priority_breakdown = summary.get('priority_breakdown', {})
        if priority_breakdown:
            prompt_parts.extend([
                "",
                "## סיכום עדיפויות:",
                f"דרישות גבוהות: {priority_breakdown.get('high', 0)}",
                f"דרישות בינוניות: {priority_breakdown.get('medium', 0)}",
                f"דרישות נמוכות: {priority_breakdown.get('low', 0)}"
            ])
        
        # Add report type specific instructions
        if report_type == "checklist":
            prompt_parts.extend([
                "",
                "## בקשה - רשימת בדיקה מפורטת:",
                "אנא הכין רשימת בדיקה מפורטת הכוללת:",
                "1. רשימת משימות לפי קטגוריות רגולטוריות",
                "2. סטטוס כל משימה (נדרש/הושלם/לא רלוונטי)",
                "3. מסמכים נדרשים לכל משימה",
                "4. מועדי יעד ריאליים",
                "5. אחראי לביצוע (בעל העסק/יועץ/ספק)",
                "6. עלות משוערת לכל משימה",
                "7. סדר עדיפויות לביצוע",
                "",
            ])
        else:  # comprehensive (default)
            prompt_parts.extend([
                "",
                "## בקשה - דוח מפורט ומקיף:",
                "אנא הכין דוח מפורט הכולל:",
                "1. סיכום מנהלים - פרופיל העסק וסיווגו",
                "2. דרישות רגולטוריות רלוונטיות מסודרות לפי עדיפות וקטגוריה",
                "3. הסבר ברור ונגיש לכל דרישה (תרגום מ'שפת חוק' לשפה עסקית)",
                "4. המלצות פעולה מעשיות עם ציר זמן",
                "5. הערכת סיכונים וזמני ביצוע ריאליים",
                "6. רשימת מסמכים נדרשים עם מקורות",
                "7. עלויות משוערות לביצוע הדרישות",
                "8. רשימת אנשי קשר רלוונטיים (רשויות, יועצים)",
                "9. לוח זמנים מפורט לביצוע",
                "10. המלצות למניעת בעיות עתידיות",
                "",
                "הדוח צריך להיות:",
                "- כתוב בעברית ברורה ונגישה",
                "- מותאם אישית לעסק הספציפי (גודל {size} מ\"ר, {seats} מקומות)",
                "- מסודר ומאורגן היטב לפי קטגוריות",
                "- מעשי וניתן לביצוע",
                "- כולל הערכות זמן ועלות ריאליות",
                "- מפרט את כל הדרישות הרלוונטיות במלואן",
                "- כתוב בפורמט טקסט פשוט ללא טבלאות (השתמש ברשימות במקום טבלאות)",
                "",
                "אנא התחל את הדוח עם כותרת מתאימה וסיכום מנהלים קצר."
            ])
        
        return "\n".join(prompt_parts)


# Singleton instance for the application
ai_service = AIService()


def generate_ai_report(business_data: Dict[str, Any], report_type: str = "comprehensive") -> AIResponse:
    """
    Convenience function to generate AI report.
    
    Args:
        business_data: Business profile and regulatory analysis results
        report_type: Type of report ("comprehensive" or "checklist")
        
    Returns:
        AIResponse with generated report
    """
    return ai_service.generate_smart_report(business_data, report_type)
