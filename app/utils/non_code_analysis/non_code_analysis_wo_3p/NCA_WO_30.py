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


def extract_key_topics_from_content(content: str) -> List[str]:
    """
    Extract key topics/themes from content using pattern matching.
    Returns meaningful topics, not generic words.
    """
    topics = []
    content_lower = content.lower()
    
    # Topic patterns - specific and meaningful
    topic_patterns = {
        "system architecture": ["architecture", "component", "module", "layer"],
        "API design": ["api", "endpoint", "rest", "graphql"],
        "database design": ["database", "schema", "table", "query"],
        "authentication and security": ["authentication", "authorization", "security", "oauth"],
        "deployment and CI/CD": ["deployment", "ci/cd", "pipeline", "docker"],
        "testing strategy": ["test", "testing", "unit test", "integration"],
        "performance optimization": ["performance", "optimization", "scalability", "caching"],
        "user interface": ["ui", "interface", "frontend", "component"],
        "data processing": ["data", "processing", "pipeline", "etl"],
        "machine learning": ["ml", "machine learning", "model", "training"],
        "cloud infrastructure": ["cloud", "aws", "azure", "kubernetes"],
        "microservices": ["microservices", "service", "distributed"],
        "event-driven architecture": ["event", "message", "queue", "kafka"],
        "requirements analysis": ["requirements", "functional", "non-functional"],
        "project planning": ["planning", "milestone", "timeline", "roadmap"],
        "code quality": ["code quality", "best practices", "standards", "review"],
    }
    
    for topic, patterns in topic_patterns.items():
        match_count = sum(1 for pattern in patterns if pattern in content_lower)
        if match_count >= 2:  # Need multiple matches for confidence
            topics.append(topic)
    
    return topics[:5]  # Top 5 topics


def extract_important_sentences(content: str, num_sentences: int = 3) -> List[str]:
    """
    Extract most important sentences using spaCy NLP.
    Prioritizes sentences with:
    - Action verbs
    - Technical entities
    - Specific details (not generic statements)
    """
    if not SPACY_AVAILABLE:
        # Fallback: use simple sentence extraction
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.split()) >= 10 and len(s.split()) <= 30]
        return sentences[:num_sentences]
    
    try:
        doc = nlp(content)
        
        # Score each sentence
        sentence_scores = []
        
        for sent in doc.sents:
            if len(sent.text.split()) < 8 or len(sent.text.split()) > 40:
                continue
            
            score = 0
            sent_lower = sent.text.lower()
            
            # Action verbs (higher score)
            action_verbs = {'develop', 'create', 'design', 'implement', 'build', 
                          'provide', 'enable', 'support', 'include', 'define'}
            verb_count = sum(1 for token in sent if token.lemma_ in action_verbs)
            score += verb_count * 3
            
            # Technical entities
            entity_count = len(sent.ents)
            score += entity_count * 2
            
            # Numbers/metrics (specific details)
            number_count = sum(1 for token in sent if token.like_num)
            score += number_count * 2
            
            # Proper nouns (specific references)
            propn_count = sum(1 for token in sent if token.pos_ == 'PROPN')
            score += propn_count * 1.5
            
            # Penalize generic/vague sentences
            generic_phrases = ['must be', 'should be', 'is important', 'it is', 
                             'this document', 'the system', 'we need', 'in order to']
            if any(phrase in sent_lower for phrase in generic_phrases):
                score -= 5
            
            # Penalize very short or very long sentences
            word_count = len(sent.text.split())
            if word_count < 10:
                score -= 3
            elif word_count > 35:
                score -= 2
            
            # Boost sentences with technical keywords
            tech_indicators = ['api', 'database', 'server', 'client', 'user', 
                             'data', 'component', 'service', 'architecture']
            tech_count = sum(1 for indicator in tech_indicators if indicator in sent_lower)
            score += tech_count * 1.5
            
            sentence_scores.append((sent.text.strip(), score))
        
        # Sort by score and return top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, score in sentence_scores[:num_sentences] if score > 0]
    
    except Exception as e:
        # Fallback
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.split()) >= 10]
        return sentences[:num_sentences]
    
# ============================================================================
# 3. IN-DEPTH BULLET POINTS (Using spaCy + Pattern Matching)
# ============================================================================

# REPLACE extract_contribution_bullets function (around line 240):

def extract_contribution_bullets(content: str, doc_type: str, metrics: Dict[str, Any]) -> List[str]:
    """
    Extract resume-ready bullets in "Developed X that Y" format.
    Action-oriented, quantified, and professional.
    100% OFFLINE - uses spaCy + pattern matching only.
    """
    bullets = []
    content_lower = content.lower()
    
    # Extract technical keywords for context
    tech_keywords = extract_technical_keywords(content)
    tech_str = ", ".join(tech_keywords[:3]) if tech_keywords else None
    
    # Generate action-oriented bullets based on document type
    if doc_type == "API_DOCUMENTATION":
        bullets.append(f"Developed comprehensive API documentation with {metrics['word_count']} words covering endpoints and specifications")
        if "authentication" in content_lower:
            bullets.append("Designed and documented authentication mechanisms including OAuth and JWT implementation")
        if "example" in content_lower or "sample" in content_lower:
            bullets.append(f"Created {metrics['code_snippet_count']} code examples demonstrating API usage patterns")
        if tech_str:
            bullets.append(f"Documented RESTful API built with {tech_str} including request/response schemas")
    
    elif doc_type == "DESIGN_DOCUMENT":
        bullets.append(f"Architected comprehensive system design documented in {metrics['word_count']}-word specification")
        if "architecture" in content_lower:
            bullets.append("Designed scalable system architecture with component diagrams and data flow specifications")
        if "database" in content_lower or "schema" in content_lower:
            bullets.append("Developed database schema and data models with entity relationships and constraints")
        if tech_str:
            bullets.append(f"Specified technical stack using {tech_str} with justification for technology choices")
        if metrics["heading_count"] >= 3:
            bullets.append(f"Structured design document into {metrics['heading_count']} organized sections covering requirements through deployment")
    
    elif doc_type == "REQUIREMENTS_DOCUMENT":
        bullets.append(f"Authored {metrics['word_count']}-word requirements specification defining project scope and deliverables")
        if "functional" in content_lower:
            bullets.append("Defined functional requirements with use cases, user stories, and acceptance criteria")
        if "non-functional" in content_lower:
            bullets.append("Specified non-functional requirements including performance benchmarks, security protocols, and scalability targets")
        if tech_str:
            bullets.append(f"Documented technical requirements for {tech_str}-based implementation")
        if metrics["bullet_point_count"] >= 5:
            bullets.append(f"Organized {metrics['bullet_point_count']} requirement items with priority levels and success metrics")
    
    elif doc_type == "TUTORIAL":
        bullets.append(f"Created {metrics['word_count']}-word tutorial with step-by-step instructions for implementation")
        if metrics["code_snippet_count"] > 0:
            bullets.append(f"Developed {metrics['code_snippet_count']} working code examples with explanations and best practices")
        if tech_str:
            bullets.append(f"Authored hands-on guide for {tech_str} covering setup through deployment")
        if "exercise" in content_lower:
            bullets.append("Designed practical exercises and challenges to reinforce learning objectives")
    
    elif doc_type == "README":
        bullets.append(f"Developed comprehensive README documentation with setup instructions and usage guidelines")
        if tech_str:
            bullets.append(f"Documented project architecture and components using {tech_str}")
        if "installation" in content_lower or "setup" in content_lower:
            bullets.append("Created detailed installation guide with prerequisites, configuration, and troubleshooting steps")
        if metrics["code_snippet_count"] > 0:
            bullets.append(f"Provided {metrics['code_snippet_count']} usage examples demonstrating core functionality")
    
    elif doc_type == "RESEARCH_DOCUMENT":
        bullets.append(f"Conducted research and authored {metrics['word_count']}-word analysis with findings and recommendations")
        if "experiment" in content_lower or "methodology" in content_lower:
            bullets.append("Designed research methodology and documented experimental procedures with data collection methods")
        if "result" in content_lower or "finding" in content_lower:
            bullets.append("Analyzed results and presented findings with statistical significance and visual representations")
        if metrics["url_count"] >= 3:
            bullets.append(f"Incorporated {metrics['url_count']} peer-reviewed sources and citations")
    
    elif doc_type == "PROPOSAL":
        bullets.append(f"Developed project proposal outlining objectives, approach, and expected outcomes")
        if tech_str:
            bullets.append(f"Proposed technical solution using {tech_str} with architecture design and implementation plan")
        if "budget" in content_lower or "timeline" in content_lower:
            bullets.append("Created project timeline with milestones, deliverables, and resource allocation")
        bullets.append(f"Authored {metrics['word_count']}-word proposal with problem statement, solution, and impact analysis")
    
    else:
        # General documentation
        bullets.append(f"Authored comprehensive documentation totaling {metrics['word_count']} words")
        if tech_str:
            bullets.append(f"Documented technical concepts and processes related to {tech_str}")
        if metrics["heading_count"] >= 3:
            bullets.append(f"Structured content into {metrics['heading_count']} well-organized sections")
        if metrics["code_snippet_count"] > 0:
            bullets.append(f"Created {metrics['code_snippet_count']} illustrative examples and code samples")
    
    # Extract actual contributions from content using spaCy
    if SPACY_AVAILABLE:
        doc = nlp(content)
        
        # Find sentences with action verbs
        action_verbs = {'develop', 'create', 'build', 'design', 'implement', 'architect', 'author'}
        
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            # Skip if too short or too long
            if len(sent.text.split()) < 8 or len(sent.text.split()) > 30:
                continue
            
            # Check for action verbs
            has_action = any(token.lemma_ in action_verbs for token in sent)
            
            # Check for technical entities
            has_tech = any(ent.label_ in ['ORG', 'PRODUCT', 'GPE'] for ent in sent.ents)
            
            # Check for quantifiable metrics
            has_numbers = any(token.like_num for token in sent)
            
            if has_action and (has_tech or has_numbers):
                # Clean up the sentence
                bullet = sent.text.strip()
                # Convert to past tense if needed
                if not any(verb in bullet.lower() for verb in ['developed', 'created', 'built', 'designed', 'implemented']):
                    # Try to convert present to past tense
                    for present, past in [('develop', 'developed'), ('create', 'created'), 
                                         ('build', 'built'), ('design', 'designed')]:
                        if present in bullet.lower():
                            bullet = bullet.replace(present, past).replace(present.title(), past.title())
                            break
                
                if not bullet.endswith('.'):
                    bullet += '.'
                
                # Only add if it's substantial and not duplicate
                if len(bullet.split()) >= 8 and not any(b.lower()[:30] == bullet.lower()[:30] for b in bullets):
                    bullets.append(bullet)
    
    # Add quantified achievement if metrics are strong
    if metrics["word_count"] >= 1000 and metrics["heading_count"] >= 5:
        bullets.append(f"Produced comprehensive {metrics['word_count']}-word document with {metrics['heading_count']} sections and {metrics['code_snippet_count']} examples")
    
    # Remove duplicates
    unique_bullets = []
    seen = set()
    for bullet in bullets:
        bullet_sig = bullet.lower()[:40]  # First 40 chars as signature
        if bullet_sig not in seen:
            seen.add(bullet_sig)
            unique_bullets.append(bullet)
    
    return unique_bullets[:8]  # Top 8 bullets


def extract_technical_keywords(content: str) -> List[str]:
    """Extract technical keywords for context (100% offline)."""
    tech_keywords = {
        "python", "javascript", "java", "typescript", "react", "angular", "vue",
        "django", "flask", "fastapi", "spring", "express", "node.js",
        "postgresql", "mongodb", "mysql", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "terraform", "jenkins", "git"
    }
    
    found = []
    content_lower = content.lower()
    for tech in tech_keywords:
        if re.search(r'\b' + tech.replace('.', r'\.') + r'\b', content_lower):
            found.append(tech.title())
    
    return found[:5]

# ============================================================================
# 4. COMPREHENSIVE SKILLS EXTRACTION
# ============================================================================

def extract_all_skills(content: str) -> Dict[str, List[str]]:
    """
    Extract ALL skills from content - technical, soft, domain-specific.
    Uses spaCy, KeyBERT, and pattern matching.
    """
    skills = {
        "technical_skills": set(),
        "soft_skills": set(),
        "domain_expertise": set(),
        "tools_and_technologies": set(),
        "writing_skills": set()
    }
    
    content_lower = content.lower()
    
    # Technical skills (programming, databases, frameworks)
    tech_keywords = {
        "python", "javascript", "java", "c++", "typescript", "go", "rust",
        "react", "angular", "vue", "django", "flask", "spring", "express",
        "postgresql", "mongodb", "mysql", "redis", "elasticsearch",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "git", "jenkins", "circleci", "github actions"
    }
    
    for tech in tech_keywords:
        if re.search(r'\b' + tech + r'\b', content_lower):
            skills["technical_skills"].add(tech.title())
    
    # Use KeyBERT for better keyword extraction
    if KEYBERT_AVAILABLE and len(content) > 100:
        try:
            keywords = kw_model.extract_keywords(content, keyphrase_ngram_range=(1, 2), top_n=20)
            for keyword, score in keywords:
                if score > 0.3:  # High relevance
                    keyword_lower = keyword.lower()
                    # Categorize
                    if any(tech in keyword_lower for tech in ["api", "system", "architecture", "design"]):
                        skills["technical_skills"].add(keyword.title())
                    elif any(word in keyword_lower for word in ["manage", "lead", "coordinate"]):
                        skills["soft_skills"].add(keyword.title())
        except:
            pass
    
    # Soft skills (enhanced detection)
    soft_skill_patterns = {
        "Technical Writing": ["documentation", "documented", "writing", "authored"],
        "System Design": ["architecture", "designed", "architected", "system design"],
        "API Design": ["api design", "endpoint design", "rest api", "graphql"],
        "Database Design": ["database design", "schema", "data model"],
        "Problem Solving": ["solved", "resolved", "addressed", "fixed"],
        "Project Planning": ["planned", "planning", "roadmap", "strategy"],
        "Requirements Analysis": ["requirements", "specifications", "analysis"],
        "Communication": ["explained", "communicated", "presented", "documented"],
        "Collaboration": ["team", "collaborated", "coordinated", "worked with"],
        "Research": ["researched", "investigated", "analyzed", "studied"],
        "Quality Assurance": ["tested", "testing", "qa", "quality"],
        "Security": ["security", "authentication", "authorization", "encryption"],
        "DevOps": ["deployment", "ci/cd", "automation", "pipeline"],
        "Agile Methodology": ["agile", "scrum", "sprint", "kanban"],
    }
    
    for skill, patterns in soft_skill_patterns.items():
        if any(pattern in content_lower for pattern in patterns):
            skills["soft_skills"].add(skill)
    
    # Domain expertise
    domain_patterns = {
        "Web Development": ["web", "frontend", "backend", "full-stack", "http"],
        "Mobile Development": ["mobile", "ios", "android", "app development"],
        "Cloud Computing": ["cloud", "aws", "azure", "serverless", "microservices"],
        "Data Science": ["data science", "machine learning", "analytics", "visualization"],
        "Cybersecurity": ["security", "encryption", "vulnerability", "penetration testing"],
        "DevOps": ["devops", "ci/cd", "containerization", "orchestration"],
        "Database Management": ["database", "sql", "nosql", "data modeling"],
        "System Architecture": ["architecture", "distributed systems", "scalability"],
        "UI/UX Design": ["ui", "ux", "user experience", "interface design"],
        "API Development": ["api", "rest", "graphql", "microservices"],
    }
    
    for domain, patterns in domain_patterns.items():
        match_count = sum(1 for pattern in patterns if pattern in content_lower)
        if match_count >= 2:
            skills["domain_expertise"].add(domain)
    
    # Writing skills (specific to documentation)
    writing_indicators = {
        "Technical Documentation": ["documentation", "technical writing"],
        "Content Creation": ["content", "article", "guide", "tutorial"],
        "Structured Writing": ["section", "heading", "organized", "structure"],
        "Clear Communication": ["explain", "describe", "clarify", "detail"],
        "Instructional Design": ["tutorial", "step-by-step", "how-to", "guide"],
        "Specification Writing": ["specification", "requirements", "criteria"],
    }
    
    for skill, indicators in writing_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            skills["writing_skills"].add(skill)
    
    # Use spaCy for entity extraction
    if SPACY_AVAILABLE:
        doc = nlp(content)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                # Check if it's a tech tool/product
                if any(tech in ent.text.lower() for tech in ["system", "platform", "tool", "service"]):
                    skills["tools_and_technologies"].add(ent.text)
    
    # Convert to sorted lists
    return {
        category: sorted(list(skill_set))
        for category, skill_set in skills.items()
    }


# ============================================================================
# 5. COMPLETENESS SCORE
# ============================================================================

def calculate_completeness_score(content: str, metrics: Dict[str, Any]) -> int:
    """
    Calculate documentation completeness score (0-100).
    Based on multiple factors.
    """
    score = 0
    
    # Content length (0-25 points)
    word_count = metrics["word_count"]
    if word_count >= 1000:
        score += 25
    elif word_count >= 500:
        score += 20
    elif word_count >= 200:
        score += 15
    elif word_count >= 100:
        score += 10
    
    # Structure - headings (0-20 points)
    heading_count = metrics["heading_count"]
    if heading_count >= 5:
        score += 20
    elif heading_count >= 3:
        score += 15
    elif heading_count >= 1:
        score += 10
    
    # Code examples (0-20 points)
    code_snippets = metrics["code_snippet_count"]
    if code_snippets >= 5:
        score += 20
    elif code_snippets >= 3:
        score += 15
    elif code_snippets >= 1:
        score += 10
    
    # References/links (0-15 points)
    url_count = metrics["url_count"]
    if url_count >= 5:
        score += 15
    elif url_count >= 3:
        score += 10
    elif url_count >= 1:
        score += 5
    
    # Bullet points/lists (0-10 points)
    bullet_count = metrics["bullet_point_count"]
    if bullet_count >= 5:
        score += 10
    elif bullet_count >= 3:
        score += 7
    elif bullet_count >= 1:
        score += 5
    
    # Paragraph structure (0-10 points)
    paragraph_count = metrics["paragraph_count"]
    if paragraph_count >= 5:
        score += 10
    elif paragraph_count >= 3:
        score += 7
    elif paragraph_count >= 1:
        score += 5
    
    return min(score, 100)


# ============================================================================
# 6. READABILITY SCORE (Using NLTK)
# ============================================================================

def calculate_readability_score(content: str) -> Dict[str, Any]:
    """
    Calculate simplified readability score.
    Returns: score/100 and readability level only.
    """
    if not NLTK_AVAILABLE:
        return {
            "score": None,
            "max_score": 100,
            "level": "unknown",
            "error": "NLTK not available"
        }
    
    try:
        # Tokenize
        sentences = sent_tokenize(content)
        words = word_tokenize(content.lower())
        words = [w for w in words if w.isalnum()]
        
        if len(sentences) == 0 or len(words) == 0:
            return {"score": 0, "max_score": 100, "level": "insufficient content"}
        
        # Calculate metrics
        total_sentences = len(sentences)
        total_words = len(words)
        total_syllables = sum(count_syllables(word) for word in words)
        
        # Average values
        avg_sentence_length = total_words / total_sentences
        avg_syllables_per_word = total_syllables / total_words
        
        # Flesch Reading Ease: 0-100 scale (already normalized)
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))
        
        # Readability level
        if flesch_reading_ease >= 80:
            level = "Very Easy (5th grade)"
        elif flesch_reading_ease >= 60:
            level = "Easy (8-9th grade)"
        elif flesch_reading_ease >= 50:
            level = "Fairly Easy (10-12th grade)"
        elif flesch_reading_ease >= 30:
            level = "Difficult (College)"
        else:
            level = "Very Difficult (Graduate)"
        
        return {
            "score": round(flesch_reading_ease, 1),
            "max_score": 100,
            "level": level
        }
    
    except Exception as e:
        return {
            "score": 0,
            "max_score": 100,
            "level": "error",
            "error": str(e)
        }
    
    # ADD this function AFTER calculate_readability_score (around line 655):

def count_syllables(word: str) -> int:
    """Count syllables in a word (simple approximation)."""
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e'):
        syllable_count -= 1
    
    # Ensure at least 1 syllable
    if syllable_count == 0:
        syllable_count = 1
    
    return syllable_count

# ============================================================================
# 7. DOCUMENT METRICS
# ============================================================================

def calculate_document_metrics(content: str) -> Dict[str, Any]:
    """Calculate comprehensive document metrics."""
    words = content.split()
    sentences = re.split(r'[.!?]+', content)
    sentences = [s for s in sentences if s.strip()]
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    
    # Count structural elements
    headings = len(re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE))
    code_blocks = len(re.findall(r'```[\w]*\n.*?```', content, re.DOTALL))
    inline_code = len(re.findall(r'`[^`]+`', content))
    urls = len(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content))
    bullet_points = len(re.findall(r'^[\s]*[-*+]\s+.+$', content, re.MULTILINE))
    numbered_lists = len(re.findall(r'^[\s]*\d+\.\s+.+$', content, re.MULTILINE))
    
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "heading_count": headings,
        "code_snippet_count": code_blocks + inline_code,
        "url_count": urls,
        "bullet_point_count": bullet_points + numbered_lists,
        "avg_words_per_sentence": round(len(words) / len(sentences), 1) if sentences else 0,
        "estimated_reading_minutes": round(len(words) / 200, 1)
    }


# ============================================================================
# 8. MAIN ANALYSIS FUNCTION
# ============================================================================

# REPLACE analyze_single_document function (around line 680):

def analyze_single_document(file_path: Path, content: str) -> Dict[str, Any]:
    """
    Complete analysis of a single document.
    Returns: file_name, document_type, summary, bullet_points, skills, 
             completeness_score, readability_score
    
    100% OFFLINE - Uses spaCy, NLTK, KeyBERT (all local)
    """
    # Calculate metrics first
    metrics = calculate_document_metrics(content)
    
    # Classify document type
    doc_type = classify_document_type(content, file_path)
    
    # Generate comprehensive summary
    summary = generate_comprehensive_summary(content, file_path.name, doc_type)
    
    # Extract bullet points (PASS METRICS)
    bullet_points = extract_contribution_bullets(content, doc_type, metrics)
    
    # Extract all skills
    skills = extract_all_skills(content)
    
    # Calculate scores
    completeness_score = calculate_completeness_score(content, metrics)
    readability_score = calculate_readability_score(content)
    
    return {
        "file_name": file_path.name,
        "document_type": doc_type,
        "summary": summary,
        "contribution_bullets": bullet_points,
        "skills": skills,
        "completeness_score": {
            "score": completeness_score,
            "max_score": 100
        },
        "readability_score": readability_score,
        "word_count": metrics["word_count"]
    }

# ============================================================================
# 9. BATCH ANALYSIS
# ============================================================================

# REPLACE the analyze_documents_batch function (around line 710):

def analyze_documents_batch(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate analysis across multiple documents."""
    if not documents:
        return {"total_documents": 0, "documents": []}
    
    # Aggregate skills
    all_skills = {
        "technical_skills": set(),
        "soft_skills": set(),
        "domain_expertise": set(),
        "tools_and_technologies": set(),
        "writing_skills": set()
    }
    
    for doc in documents:
        for category, skill_list in doc["skills"].items():
            all_skills[category].update(skill_list)
    
    all_skills = {cat: sorted(list(skills)) for cat, skills in all_skills.items()}
    
    # Aggregate bullets
    all_bullets = []
    for doc in documents:
        for bullet in doc["contribution_bullets"]:
            all_bullets.append(f"{doc['file_name']}: {bullet}")
    
    # Calculate averages - FIX: Access 'score' from dict
    avg_completeness = sum(doc["completeness_score"]["score"] for doc in documents) / len(documents)
    
    avg_readability = None
    valid_scores = [doc["readability_score"]["score"] 
                   for doc in documents 
                   if doc["readability_score"].get("score") is not None]
    if valid_scores:
        avg_readability = sum(valid_scores) / len(valid_scores)
    
    return {
        "total_documents": len(documents),
        "user_profile": {
            "all_contribution_bullets": all_bullets[:20],
            "aggregated_skills": all_skills,
            "total_unique_skills": sum(len(skills) for skills in all_skills.values()),
            "average_completeness_score": {
                "score": round(avg_completeness, 1),
                "max_score": 100
            },
            "average_readability_score": {
                "score": round(avg_readability, 1) if avg_readability else None,
                "max_score": 100
            }
        },
        "documents": documents
    }

# ============================================================================
# 10. FULL PIPELINE
# ============================================================================

def analyze_non_code_files(directory: Union[str, Path], output_path: str = None) -> Dict[str, Any]:
    """
    Complete pipeline: Classify -> Parse -> Analyze
    Reuses existing utilities from other files.
    """
    directory = Path(directory)
    
    print(f"\n🔍 Analyzing non-code files in: {directory}")
    
    # Step 1: Classify files (reuse existing function)
    classification = classify_non_code_files_with_user_verification(directory)
    files_to_analyze = classification.get("collaborative", []) + classification.get("non_collaborative", [])
    
    if not files_to_analyze:
        return {"message": "No files to analyze"}
    
    print(f"✓ Found {len(files_to_analyze)} files to analyze")
    
    # Step 2: Parse content (reuse existing function)
    parsed_data = parse_documents_to_json(files_to_analyze)
    
    # Step 3: Analyze each document
    analyzed_docs = []
    for file_data in parsed_data.get("files", []):
        if file_data.get("success"):
            try:
                analysis = analyze_single_document(Path(file_data["path"]), file_data["content"])
                analyzed_docs.append(analysis)
                print(f"✓ Analyzed: {analysis['file_name']}")
            except Exception as e:
                print(f"✗ Error analyzing {file_data['path']}: {e}")
    
    # Step 4: Batch analysis
    results = analyze_documents_batch(analyzed_docs)
    
    # Save results
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {output_path}")
    
    return results


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    from app.shared.testing_data.sample_parsed_file import sample_parsed_files
    
    # Analyze sample files
    results = []
    for file_data in sample_parsed_files["files"]:
        if file_data["success"]:
            result = analyze_single_document(Path(file_data["path"]), file_data["content"])
            results.append(result)
    
    # Batch analysis
    batch_result = analyze_documents_batch(results)
    
    # Print results
    print(json.dumps(batch_result, indent=2))