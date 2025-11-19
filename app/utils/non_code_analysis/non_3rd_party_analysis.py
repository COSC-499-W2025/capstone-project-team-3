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


# ============================================================================
# 2. COMPREHENSIVE SUMMARY (Using Sumy + spaCy)
# ============================================================================

def generate_comprehensive_summary(content: str, file_name: str, doc_type: str) -> str:
    """
    Generate comprehensive, meaningful summary using custom NLP logic.
    Uses spaCy + pattern matching for better context extraction.
    """
    content_lower = content.lower()
    
    # Extract technical keywords for context
    tech_keywords = extract_technical_keywords(content)
    tech_str = ", ".join(tech_keywords[:4]) if tech_keywords else None
    
    # Detect domain/field
    domain_keywords = {
        "Software Engineering": ["software", "code", "api", "system", "development", "application"],
        "Data Science": ["data", "analysis", "model", "dataset", "visualization", "analytics"],
        "Business": ["business", "strategy", "market", "revenue", "customer", "sales"],
        "Healthcare": ["health", "medical", "patient", "treatment", "clinical"],
        "Education": ["education", "learning", "curriculum", "student", "course"],
        "Research": ["research", "study", "experiment", "hypothesis", "findings"],
        "Design": ["design", "ui", "ux", "prototype", "wireframe", "interface"],
        "Project Management": ["project", "milestone", "deliverable", "timeline", "agile"],
    }
    
    detected_domain = None
    max_score = 0
    for domain, keywords in domain_keywords.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > max_score:
            max_score = score
            detected_domain = domain
    
    # Extract key topics/themes from content
    key_topics = extract_key_topics_from_content(content)
    
    # Get most important sentences using spaCy
    important_sentences = extract_important_sentences(content, num_sentences=3)
    
    # Build comprehensive summary
    doc_descriptions = {
        "README": "comprehensive README documentation",
        "API_DOCUMENTATION": "detailed API documentation",
        "DESIGN_DOCUMENT": "system design document outlining architecture and technical approach",
        "REQUIREMENTS_DOCUMENT": "requirements specification document",
        "TUTORIAL": "tutorial with step-by-step instructions",
        "RESEARCH_DOCUMENT": "research document with analysis and findings",
        "PROPOSAL": "project proposal",
        "GENERAL_DOCUMENTATION": "technical documentation",
        "INSTALLATION_GUIDE": "installation and setup guide",
        "MEETING_NOTES": "meeting notes and action items",
    }
    
    doc_desc = doc_descriptions.get(doc_type, "documentation")
    
    summary_parts = []
    
    # Part 1: What user created
    summary_parts.append(f"The user created {doc_desc}")
    
    # Part 2: Domain context
    if detected_domain:
        summary_parts.append(f"in the {detected_domain} domain")
    
    # Part 3: Technical stack if available
    if tech_str:
        summary_parts.append(f"using {tech_str}")
    
    # Part 4: Key topics/themes
    if key_topics:
        topics_str = ", ".join(key_topics[:3])
        summary_parts.append(f"The document covers {topics_str}")
    
    # Part 5: Add content context from important sentences
    if important_sentences:
        # Pick the most informative sentence (not too generic)
        best_sentence = None
        for sent in important_sentences:
            sent_lower = sent.lower()
            # Avoid generic sentences
            if any(generic in sent_lower for generic in ["must be", "should be", "is important", "this document"]):
                continue
            if len(sent.split()) >= 8:  # Substantial sentence
                best_sentence = sent
                break
        
        if not best_sentence and important_sentences:
            best_sentence = important_sentences[0]
        
        if best_sentence:
            if len(best_sentence) > 150:
                best_sentence = best_sentence[:150] + "..."
            summary_parts.append(f"Specifically, it addresses: {best_sentence}")
    
    # Part 6: Document scope/size
    word_count = len(content.split())
    if word_count >= 1500:
        summary_parts.append(f"The document provides comprehensive coverage with {word_count} words")
    elif word_count >= 800:
        summary_parts.append(f"The document includes {word_count} words of detailed information")
    elif word_count >= 300:
        summary_parts.append(f"The {word_count}-word document provides focused coverage")
    
    return ". ".join(summary_parts) + "."

