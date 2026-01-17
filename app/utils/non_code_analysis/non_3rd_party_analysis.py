"""
Non-code file analyzer - Using offline NLP libraries.
"""
from pathlib import Path
from typing import Dict, List, Any
import re
from collections import Counter

import spacy
from nltk.tokenize import sent_tokenize, word_tokenize
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from keybert import KeyBERT
from app.cli.user_preference_cli import UserPreferences
from app.utils.non_code_analysis.keywords.domain_keywords import (
    build_enhanced_keywords)

SPACY_AVAILABLE = True
KEYBERT_AVAILABLE = True
nlp = spacy.load("en_core_web_sm")
kw_model = None

def get_keybert_model():
    """Lazy load KeyBERT model only when needed."""
    global kw_model
    if kw_model is None:
        kw_model = KeyBERT()
    return kw_model

def classify_document_type(content: str, file_path: Path) -> str:
    """Classify document type based on content and filename."""
    content_lower = content.lower()
    file_name_lower = file_path.name.lower()

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

def generate_comprehensive_summary(content: str, file_name: str, doc_type: str) -> str:
    """ Generate comprehensive, meaningful summary using custom NLP logic. Uses spaCy + pattern matching for better context extraction."""
    content_lower = content.lower()
    tech_keywords = extract_technical_keywords(content)
    tech_str = ", ".join(tech_keywords[:4]) if tech_keywords else None
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
    key_topics = extract_key_topics_from_content(content)
    important_sentences = extract_important_sentences(content, num_sentences=3)
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
    summary_parts.append(f"The user created {doc_desc}")
    if detected_domain:
        summary_parts.append(f"in the {detected_domain} domain")
    if tech_str:
        summary_parts.append(f"using {tech_str}")
    if key_topics:
        topics_str = ", ".join(key_topics[:3])
        summary_parts.append(f"The document covers {topics_str}")
    if important_sentences:
        best_sentence = None
        for sent in important_sentences:
            sent_lower = sent.lower()
            if any(generic in sent_lower for generic in ["must be", "should be", "is important", "this document"]):
                continue
            if len(sent.split()) >= 8:
                best_sentence = sent
                break
        if not best_sentence and important_sentences:
            best_sentence = important_sentences[0]
        if best_sentence:
            if len(best_sentence) > 150:
                best_sentence = best_sentence[:150] + "..."
            summary_parts.append(f"Specifically, it addresses: {best_sentence}")
    word_count = len(content.split())
    if word_count >= 1500:
        summary_parts.append(f"The document provides comprehensive coverage with {word_count} words")
    elif word_count >= 800:
        summary_parts.append(f"The document includes {word_count} words of detailed information")
    elif word_count >= 300:
        summary_parts.append(f"The {word_count}-word document provides focused coverage")
    return ". ".join(summary_parts) + "."

def extract_technical_keywords(content: str, top_n: int = 10) -> List[str]:
    if not content or len(content.strip()) < 50:
        return []
    try:
        model = get_keybert_model()
        keywords = model.extract_keywords(
            content,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_n=top_n,
        )
        return [kw[0] for kw in keywords]
    except Exception as e:
        print(f"⚠️ KeyBERT extraction failed: {e}")
        return []

def extract_key_topics_from_content(content: str) -> List[str]:
    if not content or len(content.strip()) < 50:
        return []
    try:
        doc = nlp(content[:5000])
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        topic_counts = Counter(noun_phrases)
        top_topics = [topic for topic, _ in topic_counts.most_common(5)]
        return top_topics
    except Exception as e:
        print(f"⚠️ Topic extraction failed: {e}")
        return []

def extract_important_sentences(content: str, num_sentences: int = 3) -> List[str]:
    if not content or len(content.strip()) < 100:
        sentences = content.split(".")[:num_sentences]
        return [s.strip() + "." for s in sentences if s.strip()]
    try:
        parser = PlaintextParser.from_string(content, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, num_sentences)
        return [str(sentence) for sentence in summary_sentences]
    except Exception as e:
        print(f"⚠️ Sentence extraction failed: {e}")
        sentences = content.split(".")[:num_sentences]
        return [s.strip() + "." for s in sentences if s.strip()]

def extract_literal_tech_keywords(content: str) -> List[str]:
    techs = {
        "python", "javascript", "typescript", "react", "vue", "angular", "java",
        "fastapi", "flask", "django", "node", "node.js", "spring",
        "docker", "kubernetes", "aws", "azure", "gcp", "mongodb", "postgresql",
        "mysql", "redis", "sqlite", "git",
    }
    text = content.lower()
    return [t.title() for t in techs if re.search(rf"\b{re.escape(t)}\b", text)][:5]

def clean_content_for_bullets(text: str) -> str:
    text = re.sub(r"^\s*\d+\s*\.?\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[\.\-–]+\s*$", "", text, flags=re.MULTILINE)
    return text

def extract_contribution_bullets(content: str, doc_type: str, metrics: Dict[str, Any]) -> List[str]:
    bullets = []
    cleaned = clean_content_for_bullets(content)
    limited_content = cleaned[:1500]
    techs = extract_literal_tech_keywords(limited_content)
    tech_str = ", ".join(techs) if techs else None
    type_bullets = {
        "API_DOCUMENTATION": "Created structured API documentation outlining endpoints and request/response behavior.",
        "DESIGN_DOCUMENT": "Designed system architecture with clear components, flows, and rationale.",
        "REQUIREMENTS_DOCUMENT": "Defined functional and non-functional requirements with clear scope.",
        "TUTORIAL": "Created a step-by-step tutorial with instructions and examples.",
        "README": "Authored a complete README including setup, usage, and project structure.",
    }
    bullets.append(
        type_bullets.get(
            doc_type,
            "Produced organized documentation explaining concepts and implementation details.",
        )
    )
    if tech_str:
        bullets.append(f"Documented technical components and workflows involving {tech_str}.")
    if SPACY_AVAILABLE:
        doc = nlp(limited_content)
        action_verbs = {"develop", "design", "create", "build", "implement", "document"}
        banned_keywords = [
            "government", "critic", "echo chamber", "politic",
            "media", "society", "internet", "global", "consumer",
            "marketplace", "regulation", "framework",
        ]
        for sent in doc.sents:
            txt = sent.text.strip()
            if not (6 <= len(txt.split()) <= 25):
                continue
            if any(bad in txt.lower() for bad in banned_keywords):
                continue
            if not any(token.lemma_ in action_verbs for token in sent):
                continue
            if not txt.endswith("."):
                txt += "."
            txt = re.sub(r"\s*\d+\s*\.*$", "", txt).strip()
            bullets.append(txt)
            if len(bullets) >= 5:
                break
    if len(bullets) < 3:
        bullets.append("Provided clear explanations to support better understanding.")
    return bullets[:5]

def extract_all_skills(content: str) -> Dict[str, List[str]]:
    """
    Extract technical and soft skills from content.
    Domain expertise and tools/technologies intentionally removed.
    """

    skills = {
        "technical_skills": set(),
        "soft_skills": set(),
    }

    content_lower = content.lower()

    # ---- TECHNICAL KEYWORDS WITH CORRECT CASING ----
    TECH_CORRECT_CASING = {
        "python": "Python",
        "javascript": "JavaScript",
        "java": "Java",
        "c++": "C++",
        "typescript": "TypeScript",
        "go": "Go",
        "rust": "Rust",
        "react": "React",
        "angular": "Angular",
        "vue": "Vue",
        "django": "Django",
        "flask": "Flask",
        "spring": "Spring",
        "express": "Express",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",
        "mysql": "MySQL",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "GCP",
        "git": "Git",
        "devops": "DevOps",
        "ci/cd": "CI/CD",
        "fastapi": "FastAPI"
    }

    # Extract technical skills
    for tech_raw, tech_clean in TECH_CORRECT_CASING.items():
        if re.search(rf"\b{re.escape(tech_raw)}\b", content_lower):
            skills["technical_skills"].add(tech_clean)

    # ---- KEYBERT (OPTIONAL TECH EXTRACTION) ----
    if KEYBERT_AVAILABLE and len(content) > 100:
        try:
            keywords = kw_model.extract_keywords(content, keyphrase_ngram_range=(1, 2), top_n=20)
            for keyword, score in keywords:
                if score > 0.3:
                    kw_lower = keyword.lower()
                    if any(term in kw_lower for term in ["api", "system", "architecture", "design"]):
                        skills["technical_skills"].add(keyword.title())
        except Exception:
            pass

    # ---- SOFT SKILLS ----
    soft_skill_patterns = {
        "Communication": ["explained", "communicated", "documented", "presented"],
        "Collaboration": ["team", "collaborated", "worked with"],
        "Problem Solving": ["solved", "resolved", "addressed"],
        "Project Planning": ["planned", "planning", "roadmap", "strategy"],
        "Quality Assurance": ["tested", "testing", "qa", "quality"],
        "Requirements Analysis": ["requirements", "analysis", "specification"]
    }

    for skill, patterns in soft_skill_patterns.items():
        if any(p in content_lower for p in patterns):
            skills["soft_skills"].add(skill)

    return {k: sorted(list(v)) for k, v in skills.items()}


def calculate_completeness_score(content: str, doc_type: str) -> int:
    """
    Document-type–aware completeness scoring (0–100). Each document type has its own expected conceptual components. We check how many of those components are present in the text.
    This is NOT structural (headings/urls/etc). It is semantic completeness.
    """

    if not content or len(content.strip()) < 30:
        return 0

    text = content.lower()

    # --- Expected sections for each documentation type ---
    SECTION_PATTERNS = {
        "PROPOSAL": [
            "problem", "objective", "goal", "purpose",
            "approach", "solution",
            "milestone", "timeline",
            "risk", "challenge", "mitigation"
        ],
        "DESIGN_DOCUMENT": [
            "architecture", "design", "component",
            "module", "flow", "diagram",
            "rationale", "pattern"
        ],
        "REQUIREMENTS_DOCUMENT": [
            "functional requirement", "non-functional",
            "criteria", "constraint", "must", "should"
        ],
        "API_DOCUMENTATION": [
            "endpoint", "request", "response",
            "method", "parameter", "authentication"
        ],
        "README": [
            "introduction", "install", "setup",
            "usage", "example", "feature"
        ],
        "TUTORIAL": [
            "step", "instruction", "guide",
            "example", "walkthrough"
        ],
        "RESEARCH_DOCUMENT": [
            "research", "study", "experiment",
            "analysis", "hypothesis", "finding"
        ],
        "INSTALLATION_GUIDE": [
            "install", "setup", "configuration",
            "environment", "dependency"
        ],
        "MEETING_NOTES": [
            "agenda", "notes", "discussion",
            "action item", "decision"
        ],

        # Fallback: general documentation expectations
        "GENERAL_DOCUMENTATION": [
            "overview", "explain", "describe",
            "details", "note", "discussion"
        ]
    }

    # Select patterns based on doc type, default to general
    patterns = SECTION_PATTERNS.get(doc_type, SECTION_PATTERNS["GENERAL_DOCUMENTATION"])

    found = 0
    for kw in patterns:
        if kw in text:
            found += 1

    if not patterns:
        return 0

    completeness = int((found / len(patterns)) * 100)
    return min(max(completeness, 0), 100)

from typing import Dict, Any, List
from collections import Counter
from pathlib import Path
import re
from app.cli.user_preference_cli import UserPreferences
from app.utils.non_code_analysis.keywords.domain_keywords import build_enhanced_keywords


def analyze_project_clean(parsed_files: Dict[str, Any], email: str = None) -> Dict[str, Any]:
    """
    Clean project-wide analysis with optional user preference integration.
    
    Args:
        parsed_files: Dictionary containing parsed file data
        email: Optional user email to load preferences (used ONLY for keyword detection)
    """
    
    # Load user preferences if email provided (ONLY for keyword detection)
    user_prefs = None
    if email:
        pref_manager = UserPreferences()
        user_prefs = pref_manager.get_latest_preferences(email)
        if user_prefs:
            print(f"✅ Using preferences for enhanced keyword detection")
            print(f"   Industry: {user_prefs.get('industry')}")
            print(f"   Job Title: {user_prefs.get('job_title')}")
    
    # Handle both "files" and "parsed_files" keys for compatibility
    files = parsed_files.get("parsed_files") or parsed_files.get("files", [])
    
    if not files:
        return {
            "project_summary": "No files were available for analysis.",
            "resume_bullets": [],
            "skills": {
                "technical_skills": [],
                "soft_skills": []
            },
            "Metrics": {
                "completeness_score": 0,
                "word_count": 0,
                "contribution_activity": {
                    "doc_type_counts": {},
                    "doc_type_frequency": {}
                }
            },
            "user_context": {
                "detected_domain": None,
                "domain_match": False,
                "industry": user_prefs.get('industry') if user_prefs else None,
                "job_title": user_prefs.get('job_title') if user_prefs else None
            } if user_prefs else None
        }

    project_content = ""
    project_skills = {
        "technical_skills": set(),
        "soft_skills": set(),
    }
    doc_type_counts: Counter = Counter()
    doc_type_freq: Counter = Counter()
    files_by_doc_type = []

    for file_data in files:
        if not file_data.get("success", False):
            continue
        content = (file_data.get("content") or "").strip()
        if not content:
            continue
        project_content += "\n\n" + content
        file_path = Path(file_data.get("path", file_data.get("name", "unknown.txt")))
        doc_type = classify_document_type(content, file_path)
        freq = file_data.get("contribution_frequency", 1)
        
        doc_type_counts[doc_type] += 1
        doc_type_freq[doc_type] += freq
        
        files_by_doc_type.append({
            "file_name": file_data.get("name", ""),
            "file_path": str(file_path),
            "doc_type": doc_type,
            "contribution_frequency": freq
        })
        
        file_skills = extract_all_skills(content)
        for cat, vals in file_skills.items():
            project_skills[cat].update(vals)

    if not project_content.strip():
        return {
            "project_summary": "No successfully parsed content was available for analysis.",
            "resume_bullets": [],
            "skills": {
                "technical_skills": [],
                "soft_skills": [],
            },
            "Metrics": {
                "completeness_score": 0,
                "word_count": 0,
                "contribution_activity": {
                    "doc_type_counts": {},
                    "doc_type_frequency": {}
                }
            },
            "user_context": {
                "detected_domain": None,
                "domain_match": False,
                "industry": user_prefs.get('industry') if user_prefs else None,
                "job_title": user_prefs.get('job_title') if user_prefs else None
            } if user_prefs else None
        }

    project_content_lower = project_content.lower()

    doc_descriptions = {
        "README": "README documentation",
        "API_DOCUMENTATION": "API documentation",
        "DESIGN_DOCUMENT": "system design and architecture documentation",
        "REQUIREMENTS_DOCUMENT": "requirements documentation",
        "TUTORIAL": "tutorial or how-to documentation",
        "RESEARCH_DOCUMENT": "research or analysis documents",
        "PROPOSAL": "project proposal documents",
        "GENERAL_DOCUMENTATION": "general technical documentation",
        "INSTALLATION_GUIDE": "installation and setup guides",
        "MEETING_NOTES": "meeting notes and action items",
    }

    if doc_type_counts:
        top_doc_types = [dt for dt, _ in doc_type_counts.most_common(2)]
    else:
        top_doc_types = ["GENERAL_DOCUMENTATION"]

    doc_phrases = [doc_descriptions.get(dt, "documentation") for dt in top_doc_types]
    if len(doc_phrases) == 1:
        doc_phrase = doc_phrases[0]
    else:
        doc_phrase = ", ".join(doc_phrases[:-1]) + " and " + doc_phrases[-1]

    
    # Build keywords with user preferences
    user_industry = user_prefs.get('industry') if user_prefs else None
    user_job_title = user_prefs.get('job_title') if user_prefs else None
    
    domain_keywords = build_enhanced_keywords(user_industry, user_job_title)

    # Weighted scoring with user preference boost
    detected_domains = {}
    for domain, kws in domain_keywords.items():
        score = sum(1 for kw in kws if kw in project_content_lower)
        
        # Boost score if domain matches user's industry (1.5x multiplier)
        if user_industry and domain.lower() == user_industry.lower():
            score = score * 1.5
        
        if score > 0:
            detected_domains[domain] = score

    # Find highest scoring domain
    detected_domain = None
    if detected_domains:
        detected_domain = max(detected_domains.items(), key=lambda x: x[1])[0]
    

    has_architecture = any(w in project_content_lower for w in ["architecture", "design", "microservice", "event-driven"])
    has_requirements = any(w in project_content_lower for w in ["requirement", "requirements", "specification", "non-functional"])
    has_nlp_or_parsing = any(
        w in project_content_lower
        for w in ["parse", "parser", "nlp", "natural language", "skill extraction", "contribution analysis", "analytics platform"]
    )
    has_risks_or_testing = any(w in project_content_lower for w in ["risk", "mitigation", "testing", "performance", "latency", "uptime"])

    summary_parts = []
    summary_parts.append(f"Across this project, the user created {doc_phrase}.")
    
    if detected_domain:
        summary_parts.append(f"The documentation is primarily in the {detected_domain} domain.")
    
    if has_architecture:
        summary_parts.append("It describes the system architecture and key design decisions.")
    if has_requirements:
        summary_parts.append("It captures core functional and non-functional requirements for the platform.")
    if has_nlp_or_parsing:
        summary_parts.append("It outlines parsing, analysis, and NLP-driven capabilities for working with non-code artifacts.")
    if has_risks_or_testing:
        summary_parts.append("It also discusses risks, testing, and reliability or performance considerations.")
    
    if len(summary_parts) == 1:
        summary_parts.append("The documents collectively describe the goals, behaviour, and constraints of the project.")
    
    final_summary = " ".join(part.strip() for part in summary_parts)

    bullets: List[str] = []
    if has_architecture:
        bullets.append("Designed or documented the system architecture and overall platform structure.")
    if has_requirements:
        bullets.append("Specified functional and non-functional requirements for how the platform should behave.")
    if has_nlp_or_parsing:
        bullets.append("Outlined parsing and NLP-based analysis of non-code artifacts to extract skills and contributions.")
    if has_risks_or_testing:
        bullets.append("Identified key risks, mitigation strategies, and testing or performance considerations.")

    tech_skills_sorted = sorted(project_skills["technical_skills"])
    if tech_skills_sorted:
        top_tech = tech_skills_sorted[:5]
        bullets.append(f"Worked with technologies such as {', '.join(top_tech)}.")
    
    main_doc_type = top_doc_types[0] if top_doc_types else "GENERAL_DOCUMENTATION"

    metrics = {
        "word_count": len(project_content.split()),
        "heading_count": len(re.findall(r"^#{1,6}\s+.+$", project_content, re.MULTILINE)),
        "code_snippet_count": len(re.findall(r"```[\w]*\n.*?```", project_content, re.DOTALL)),
        "url_count": len(re.findall(r"https?://[^\s\)\]]+", project_content)),
        "bullet_point_count": len(re.findall(r"^\s*[\-\*\+]\s+", project_content, re.MULTILINE)),
        "paragraph_count": len([p for p in re.split(r"\n{2,}", project_content) if len(p.strip().split()) > 10])
    }
    completeness_score = calculate_completeness_score(project_content, main_doc_type)

    extracted_bullets = extract_contribution_bullets(project_content, main_doc_type, metrics)

    seen_bullets = set(bullets)
    for b in extracted_bullets:
        b_clean = b.strip()
        if b_clean and b_clean not in seen_bullets:
            bullets.append(b_clean)
            seen_bullets.add(b_clean)
        if len(bullets) >= 5:
            break

    bullets = bullets[:5]

    final_skills = {
        category: sorted(list(skill_set))
        for category, skill_set in project_skills.items()
    }

    return {
        "project_summary": final_summary.strip(),
        "resume_bullets": bullets,
        "skills": final_skills,
        "Metrics": {
            "completeness_score": completeness_score,
            "word_count": len(project_content.split()),
            "contribution_activity": {
                "doc_type_counts": dict(doc_type_counts),
                "doc_type_frequency": dict(doc_type_freq)
            }
        },
        "user_context": {
            "detected_domain": detected_domain,
            "domain_scores": detected_domains, 
            "domain_match": detected_domain and user_prefs and detected_domain.lower() == user_prefs.get('industry', '').lower(),
            "industry": user_prefs.get('industry') if user_prefs else None,
            "job_title": user_prefs.get('job_title') if user_prefs else None,
            "keywords_used": len(domain_keywords.get(detected_domain, [])) if detected_domain else 0
        } if email else None 
    }
