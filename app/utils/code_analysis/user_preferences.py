"""
User preference utilities for code analysis.
Handles loading and applying user preferences to enhance analysis results.
"""
from typing import Dict, List, Optional
from .patterns.tech_patterns import TechnicalPatterns


def load_user_preferences(email: Optional[str]) -> Optional[Dict]:
    """Load user preferences if email provided. Returns None if not available."""
    if not email:
        return None
    
    try:
        from app.cli.user_preference_cli import UserPreferences
        pref_manager = UserPreferences()
        user_prefs = pref_manager.get_latest_preferences(email)
        
        if user_prefs:
            print(f"✅ Enhancing code analysis with user preferences")
            print(f"   Industry: {user_prefs.get('industry')} | Job Title: {user_prefs.get('job_title')}")
        
        return user_prefs
    except ImportError:
        print("⚠️  User preferences not available - using standard analysis")
        return None


def get_preference_weighted_keywords(base_keywords: List[str], user_prefs: Optional[Dict]) -> List[str]:
    """
    Reorder and prioritize keywords based on user preferences for better relevance.
    Instead of adding new keywords, this focuses on highlighting the most relevant ones.
    """
    if not user_prefs or not base_keywords:
        return base_keywords
    
    # Score keywords based on relevance using shared patterns
    keyword_scores = {}
    for keyword in base_keywords:
        score = 1.0  # Default score
        
        # Boost score based on industry
        industry = user_prefs.get('industry', '')
        # Case-insensitive lookup for industry priorities
        industry_key = None
        for key in TechnicalPatterns.INDUSTRY_KEYWORD_PRIORITIES.keys():
            if industry.lower() == key.lower():
                industry_key = key
                break
        
        if industry_key:
            priorities = TechnicalPatterns.INDUSTRY_KEYWORD_PRIORITIES[industry_key]
            if any(term in keyword.lower() for term in priorities.get("high", [])):
                score *= 2.0
            elif any(term in keyword.lower() for term in priorities.get("medium", [])):
                score *= 1.5
        
        # Boost score based on job title
        job_title = user_prefs.get('job_title', '').lower()
        for job_key, terms in TechnicalPatterns.JOB_KEYWORD_PRIORITIES.items():
            if job_key in job_title:
                if any(term in keyword.lower() for term in terms):
                    score *= 1.5
                break
        
        keyword_scores[keyword] = score
    
    # Return keywords sorted by relevance score (highest first), then alphabetically
    return sorted(base_keywords, key=lambda k: (-keyword_scores[k], k))


def enhance_resume_bullets_with_preferences(base_bullets: List[str], user_prefs: Optional[Dict], metrics: Dict) -> List[str]:
    """
    Enhance resume bullets to be more targeted to user's career goals.
    Focus on emphasizing relevant skills and experiences.
    """
    if not user_prefs or not base_bullets:
        return base_bullets
    
    industry = user_prefs.get('industry', '').lower()
    job_title = user_prefs.get('job_title', '').lower()
    
    enhanced_bullets = []
    for bullet in base_bullets:
        enhanced_bullet = bullet
        
        # Add industry-specific emphasis where appropriate using shared patterns
        for ind_key, emphasis_terms in TechnicalPatterns.INDUSTRY_RESUME_ENHANCEMENTS.items():
            if ind_key in industry:
                # Replace generic terms with more specific ones
                if "comprehensive" in enhanced_bullet.lower() and ind_key == "software engineering":
                    enhanced_bullet = enhanced_bullet.replace("comprehensive", "scalable and maintainable")
                elif "analysis" in enhanced_bullet.lower() and ind_key == "data science":
                    enhanced_bullet = enhanced_bullet.replace("analysis", "data-driven analysis")
                break
        
        # Prioritize job-relevant action verbs using shared patterns
        for job_key, action_verbs in TechnicalPatterns.JOB_ACTION_VERBS.items():
            if job_key in job_title:
                # If bullet starts with generic terms, try to use more specific ones
                if enhanced_bullet.lower().startswith("created") and "engineered" in action_verbs:
                    enhanced_bullet = enhanced_bullet.replace("Created", "Engineered", 1)
                elif enhanced_bullet.lower().startswith("worked on") and "developed" in action_verbs:
                    enhanced_bullet = enhanced_bullet.replace("Worked on", "Developed", 1)
                break
        
        enhanced_bullets.append(enhanced_bullet)
    
    return enhanced_bullets


def prioritize_patterns_by_preferences(patterns: Dict, user_prefs: Optional[Dict]) -> Dict:
    """
    Reorder detected patterns to emphasize those most relevant to user's career goals.
    """
    if not user_prefs:
        return patterns
    
    industry = user_prefs.get('industry', '').lower()
    job_title = user_prefs.get('job_title', '').lower()
    
    enhanced_patterns = patterns.copy()
    
    # Reorder patterns based on relevance using shared pattern priorities
    for category in ["design_patterns", "architectural_patterns", "frameworks_detected"]:
        if category in enhanced_patterns:
            current_items = enhanced_patterns[category]
            if current_items:
                # Get priority items for this category and industry
                priority_items = []
                for ind_key, priorities in TechnicalPatterns.PATTERN_PRIORITIES.items():
                    if ind_key in industry and category.replace("_detected", "") in priorities:
                        priority_items = priorities[category.replace("_detected", "")]
                        break
                
                # Reorder: priority items first, then others
                prioritized = []
                remaining = list(current_items)
                
                for priority_item in priority_items:
                    for item in current_items:
                        if priority_item.lower() in item.lower() and item not in prioritized:
                            prioritized.append(item)
                            if item in remaining:
                                remaining.remove(item)
                
                enhanced_patterns[category] = prioritized + remaining
    
    return enhanced_patterns