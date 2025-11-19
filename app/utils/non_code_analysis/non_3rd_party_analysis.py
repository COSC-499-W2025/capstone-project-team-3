"""
Non-code file analyzer - Using offline NLP libraries.
Provides: Summary, Bullet Points, Skills, Completeness Score, Readability Score

Libraries used:
- spaCy: Entity recognition, POS tagging
- NLTK: Readability scores
- TextBlob: Sentiment analysis
- KeyBERT: Keyword extraction
- sumy: Text summarization
"""

from pathlib import Path
from typing import Dict, List, Any, Union
import json
import re
from collections import Counter

# NLP Libraries
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy not available")

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    nltk.download('punkt', quiet=True)
    nltk.download('cmudict', quiet=True)
    NLTK_AVAILABLE = True
except:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK not available")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except:
    TEXTBLOB_AVAILABLE = False
    print("⚠️ TextBlob not available")

try:
    from keybert import KeyBERT
    kw_model = KeyBERT()
    KEYBERT_AVAILABLE = True
except:
    KEYBERT_AVAILABLE = False
    print("⚠️ KeyBERT not available")

try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    SUMY_AVAILABLE = True
except:
    SUMY_AVAILABLE = False
    print("⚠️ Sumy not available")

# Reuse existing utilities
from app.utils.non_code_parsing.document_parser import parse_documents_to_json
from app.utils.non_code_analysis.non_code_file_checker import classify_non_code_files_with_user_verification

# Reuse code analysis patterns
# ============================================================================
# 1. DOCUMENT TYPE CLASSIFICATION
# ============================================================================

def classify_document_type(content: str, file_path: Path) -> str:
    """Classify document type based on content and filename."""
    content_lower = content.lower()
    file_name_lower = file_path.name.lower()
    
    # Filename patterns
    filename_patterns = {
        "README": ["readme"],
        "CHANGELOG": ["changelog", "history", "releases"],
        "LICENSE": ["license", "copying"],
        "CONTRIBUTING": ["contributing"],
        "TODO": ["todo"],
        "MEETING_NOTES": ["meeting", "notes", "minutes"],
    }
    
    for doc_type, patterns in filename_patterns.items():
        if any(pattern in file_name_lower for pattern in patterns):
            return doc_type
    
    # Content patterns
    if any(word in content_lower for word in ["api", "endpoint", "request", "response"]) and content_lower.count("api") >= 3:
        return "API_DOCUMENTATION"
    
    if any(word in content_lower for word in ["install", "setup", "getting started"]):
        return "INSTALLATION_GUIDE"
    
    if "tutorial" in content_lower or "step-by-step" in content_lower:
        return "TUTORIAL"
    
    if "requirements" in content_lower and "specification" in content_lower:
        return "REQUIREMENTS_DOCUMENT"
    
    if "design" in content_lower and "architecture" in content_lower:
        return "DESIGN_DOCUMENT"
    
    if any(word in content_lower for word in ["research", "study", "experiment", "hypothesis"]):
        return "RESEARCH_DOCUMENT"
    
    if any(word in content_lower for word in ["proposal", "plan", "strategy"]):
        return "PROPOSAL"
    
    return "GENERAL_DOCUMENTATION"
