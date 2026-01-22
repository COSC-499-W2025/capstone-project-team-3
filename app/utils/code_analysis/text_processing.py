"""
Text processing utilities for code analysis.
Contains shared helpers for parsing and cleaning text data.
"""
import re
from typing import Set, List
from .patterns.tech_patterns import TechnicalPatterns


def split_camelcase_and_filter(text: str, min_length: int = 2) -> Set[str]:
    """
    Helper: Split camelCase/snake_case text and filter by length.
    Shared logic for both GitHub and parsed file keyword extraction.
    """
    if not text or len(text) <= min_length:
        return set()
    
    # Split camelCase and snake_case
    words = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', text)
    
    # Filter by length and common terms
    filtered_words = {
        word.lower() for word in words 
        if len(word) > min_length and word.lower() not in TechnicalPatterns.COMMON_TERMS
    }
    
    return filtered_words


def extract_meaningful_filename_keywords(filenames: List[str]) -> Set[str]:
    """
    Helper: Extract meaningful keywords from file names and paths.
    Shared logic for processing file paths.
    """
    tech_terms = set()
    
    for filename in filenames:
        # Extract from file path segments
        for segment in filename.split('/'):
            if segment and '.' not in segment:  # Skip file extensions
                tech_terms.update(split_camelcase_and_filter(segment))
        
        # Extract from filename without extension
        if '/' in filename:
            filename = filename.split('/')[-1]
        if '.' in filename:
            filename = filename.split('.')[0]
        
        tech_terms.update(split_camelcase_and_filter(filename))
    
    return tech_terms


def get_top_keywords(keywords: Set[str], limit: int = 15) -> List[str]:
    """
    Helper: Get top keywords sorted alphabetically.
    Shared logic for returning final keyword lists.
    """
    return sorted(list(keywords))[:limit]