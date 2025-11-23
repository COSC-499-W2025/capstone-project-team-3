"""
Non-code file analyzer - Using offline NLP libraries.
"""
from pathlib import Path
from typing import Dict, List, Any
import re
from collections import Counter

# NLP Libraries - Direct imports
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from keybert import KeyBERT

# Load only spaCy at import
nlp = spacy.load("en_core_web_sm")
kw_model = None  # Lazy load

def get_keybert_model():
    """Lazy load KeyBERT model only when needed."""
    global kw_model
    if kw_model is None:
        kw_model = KeyBERT()
    return kw_model

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

# ADD THESE FUNCTIONS BEFORE generate_comprehensive_summary:
def extract_technical_keywords(content: str, top_n: int = 10) -> List[str]:
    if not content or len(content.strip()) < 50:
        return []
    
    try:
        model = get_keybert_model()  # Load here instead
        keywords = model.extract_keywords(
            content,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=top_n
        )
        return [kw[0] for kw in keywords]
    except Exception as e:
        print(f"⚠️ KeyBERT extraction failed: {e}")
        return []


def extract_key_topics_from_content(content: str) -> List[str]:
    """Extract key topics using spaCy NER and noun phrases."""
    if not content or len(content.strip()) < 50:
        return []
    
    try:
        doc = nlp(content[:5000])  # Limit for performance
        
        # Extract noun phrases (topics)
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Count frequency and get top topics
        topic_counts = Counter(noun_phrases)
        top_topics = [topic for topic, _ in topic_counts.most_common(5)]
        
        return top_topics
    except Exception as e:
        print(f"⚠️ Topic extraction failed: {e}")
        return []


def extract_important_sentences(content: str, num_sentences: int = 3) -> List[str]:
    """Extract most important sentences using Sumy LSA summarizer."""
    if not content or len(content.strip()) < 100:
        sentences = content.split('.')[:num_sentences]
        return [s.strip() + '.' for s in sentences if s.strip()]
    
    try:
        parser = PlaintextParser.from_string(content, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, num_sentences)
        return [str(sentence) for sentence in summary_sentences]
    except Exception as e:
        print(f"⚠️ Sentence extraction failed: {e}")
        # Fallback: return first few sentences
        sentences = content.split('.')[:num_sentences]
        return [s.strip() + '.' for s in sentences if s.strip()]
    