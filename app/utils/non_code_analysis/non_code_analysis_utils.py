import re
from pathlib import Path
from typing import List, Dict
from collections import Counter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Send non code parsed content using Sumy LSA Local Pre-processing IF the file exceeds token limit 
#  *This step uses Sumy LSA summarizer (runs locally, no external API calls needed)

def pre_process_non_code_files(parsed_files: Dict, max_content_length: int = 50000, language: str = "english") -> List[Dict]:
    """
    This function pre-processes parsed project data using Sumy LSA summarizer to generate 
    concise file summaries and extract key topics for the second LLM to use.

    This is a local preprocessing step that uses Sumy LSA Natural Language Processing (runs locally, no external API calls needed).
    
    Arguments:
        parsed_files: JSON object from parse_documents_to_json 
        max_file_size_mb: Maximum file size in MB to process (default: 5.0 MB)
        max_content_length: Maximum content length in characters to process (default: 50000)
        summary_sentences: Number of sentences to include in summary (default: 3)
        language: Language for tokenization and summarization (default: "english")
    
    Returns:
        List of llm1_summary dictionaries, each with structure:
        {
            "key_topics": ["topic1", "topic2", ...],
            "summary": "concise summary text",
            "file_name": "original file name",
        }
    """
    llm1_summaries = []
    
    # Extract files list from parsed_files
    files = parsed_files.get("files", [])
    
    for file_data in files:
        # Skip files that weren't successfully parsed
        if not file_data.get("success", False):
            continue
        
        file_path_str = file_data.get("path", "")
        file_name = file_data.get("name", "")
        content = file_data.get("content", "")
        
        # Check file size
        # TODO : Intergrate file size check rather than content length if needed
        # Check content length
        if len(content) > max_content_length:
            print(f"Warning: Content for {file_name} exceeds {max_content_length} characters. Truncating...")
            content = content[:max_content_length] + "... [truncated]"
        
        # Skip empty content
        if not content or not content.strip():
            continue
        
        # Dynamically determine the number of summary sentences
        content_length = len(content)
        if content_length < 1000:
            summary_sentences = 3
        elif content_length < 5000:
            summary_sentences = 5
        elif content_length < 10000:
            summary_sentences = 10
        else:
            summary_sentences = 15
        
        # Generate summary and key topics using Sumy LSA
        try:
            # Generate summary using Sumy LSA
            summary = _sumy_lsa_summarize(content, num_sentences=summary_sentences, language=language)
            
            # Extract key topics using frequency analysis
            key_topics = _extract_key_topics_frequency(content, num_topics=5)
            
            if not key_topics:
                raise ValueError("Could not extract key topics from content")

            llm1_summary = {
                "key_topics": key_topics[:5],  # Limit to 5 main topics
                "summary": summary.strip(),
                "file_name": file_name,
                "file_path": file_path_str
            }
            
            llm1_summaries.append(llm1_summary)
            
        except Exception as e:
            print(f"Error processing {file_name} with Sumy LSA: {e}")
            # Continue with next file
            continue
    
    return llm1_summaries

def _sumy_lsa_summarize(content: str, num_sentences: int, language: str = "english") -> str:
    """
    Generate summary using Sumy LSA (Latent Semantic Analysis) summarizer.
    
    Args:
        content: Document content to summarize
        num_sentences: Number of sentences to include in summary
        language: Language for tokenization (default: "english")
    
    Returns:
        Summary string
    
    Raises:
        ImportError: If Sumy is not available
        Exception: If NLTK tokenizers are missing or other errors occur
    """
    
    try:
        # Create parser from plain text
        parser = PlaintextParser.from_string(content, Tokenizer(language))
        
        # Create LSA summarizer
        summarizer = LsaSummarizer(Stemmer(language))
        summarizer.stop_words = get_stop_words(language)
        
        # Generate summary
        summary_sentences = summarizer(parser.document, num_sentences)
        
        # Join sentences into a single string
        summary = ' '.join(str(sentence) for sentence in summary_sentences)
        return summary.strip()
    except Exception as e:
        print(f"Error generating summary with Sumy LSA: {e}")

def _extract_key_topics_frequency(content: str, num_topics: int = 5) -> List[str]:
    """
    Extract key topics using word frequency analysis.
    
    Args:
        content: Document content
        num_topics: Number of key topics to extract
    
    Returns:
        List of key topics/phrases
    """
    # Normalize and tokenize text
    words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can'
    }
    
    # Filter stop words and short words
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count word frequencies
    word_freq = Counter(filtered_words)
    
    # Extract bigrams (two-word phrases) for better topic extraction
    bigrams = []
    for i in range(len(filtered_words) - 1):
        bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
        bigrams.append(bigram)
    
    bigram_freq = Counter(bigrams)
    
    # Combine single words and bigrams, weighted
    topic_scores = {}
    
    # Add single words
    for word, freq in word_freq.items():
        topic_scores[word] = freq
    
    # Add bigrams with higher weight
    for bigram, freq in bigram_freq.items():
        topic_scores[bigram] = freq * 1.5
    
    # Get top topics
    top_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Extract unique topics (avoid substrings)
    selected_topics = []
    seen_words = set()
    
    for topic, score in top_topics:
        # Skip if topic is a substring of already selected topic
        is_substring = any(topic in st or st in topic for st in selected_topics)
        if not is_substring and topic not in seen_words:
            selected_topics.append(topic)
            seen_words.add(topic)
            if len(selected_topics) >= num_topics:
                break
    
    # Capitalize first letter of each word
    formatted_topics = []
    for topic in selected_topics:
        formatted = ' '.join(word.capitalize() for word in topic.split())
        formatted_topics.append(formatted)
    
    return formatted_topics

#TODO Step 3: Aggregate non code summaries into a single analyzable project
def aggregate_non_code_summaries(llm1_summary):
    """
    This function aggregates the preprocssed llm1 summary of non-code files into one single project for
    the second LLM to analyze.
    Returns aggregated_project.
    """
    pass

#TODO Step 4: Generate prompt for second LLM (Take into account user preferences in PROMPT)
def create_non_code_analysis_prompt(aggregated_project, llm2_metrics):
    """
    Create a structured prompt for AI agent analysis using the aggregated llm1 summaries.
    Returns formatted prompt string that follows the structure of llm2_metrics.
    """
    pass

#TODO Step 5: Analyze summries using the second LLM
def generate_non_code_insights(PROMPT):
    """
    Generates llm2_metrics by calling LLM2 with the formatted prompt.
    Returns Final_Result
    """
    pass

#TODO Step 6: Store results
def store_non_code_analysis_results(final_result):
    """
    Store analysis results in RESUME table and SKILLS table in database.
    """
    pass

def analyze_non_code_files(parsed_files):
    """
    Entry & Main Flow: pre-process files (NLP), aggregate summaries, generate prompt,
    call LLM2, store analysis results.
    """
    # 1. Pre-Process files (Use LLM1)
    pre_process_non_code_files(parsed_files)

    # 2. Aggregate summaries 
    aggregate_non_code_summaries(llm1_summary)
    
    # 3. Generate Analysis Prompt
    create_non_code_analysis_prompt(aggregated_project)
    
    # 4. Call LLM2 for Analysis
    generate_non_code_insights(PROMPT)

    # 5. Store Data
    store_non_code_analysis_results(Final_Result)


# Hardcoded function for CLI run
if __name__ == "__main__":
    # Sample parsed_files object matching the structure from document_parser
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/project_proposal.pdf",
                "name": "project_proposal.pdf",
                "type": "pdf",
                "content": """Project Overview: This proposal outlines a comprehensive event-driven analytics platform for Team 3. 
                The system will ingest non-code artifacts to derive resume-ready highlights and map extracted content to skills and contributions.
                
                System Architecture: The platform uses an event-driven architecture with queue-based decoupling. 
                This design ensures scalability and maintainability. The system consists of multiple microservices that communicate through message queues.
                
                Key Features: The platform includes document parsing capabilities for PDF, DOCX, and text files. 
                It implements natural language processing for skill extraction and contribution analysis. 
                The system provides a dashboard for visualizing project insights and generating resume summaries.
                
                Milestones: The project is divided into four main milestones. 
                M1 focuses on requirements gathering and system design. 
                M2 implements core parsing and analysis functionality. 
                M3 adds advanced NLP and visualization features. 
                M4 focuses on testing, optimization, and deployment.
                
                Risks and Mitigation: Key risks include data latency issues and OCR quality concerns. 
                We will mitigate these through careful system design and robust error handling. 
                Performance testing will be conducted throughout development.
                
                Team Roles: The team consists of backend developers, frontend developers, and a project manager. 
                Each member has specific responsibilities aligned with their expertise areas.""",
                "success": True,
                "error": ""
            },
            {
                "path": "/test/requirements_doc.txt",
                "name": "requirements_doc.txt",
                "type": "txt",
                "content": """Requirements Document for Analytics Platform
                
                Functional Requirements:
                1. The system must parse PDF, DOCX, and text files
                2. The system must extract key topics and generate summaries
                3. The system must identify skills and contributions from documents
                4. The system must provide a user-friendly dashboard interface
                
                Non-Functional Requirements:
                1. The system must process documents within 5 seconds
                2. The system must support files up to 5MB in size
                3. The system must maintain 99% uptime
                4. The system must be secure and protect user data
                
                Technical Stack: Python, FastAPI, React, PostgreSQL, Docker
                Development Timeline: 12 weeks with 4 major milestones
                Success Criteria: All functional requirements met, positive user feedback""",
                "success": True,
                "error": ""
            },
            {

                "path":   "/files/file_three.txt",
                "name": "file_three.pdf",
                "type": "txt",
                "content" : """Artificial intelligence (AI) has transformed nearly every industry in the 21st century. 
                From self-driving cars to medical diagnostics, AI-driven systems are capable of processing 
                vast amounts of data and identifying complex patterns that humans might overlook. 
                However, while the potential of AI is immense, the challenges that accompany it are equally significant. 
                Issues surrounding ethics, data privacy, and algorithmic bias have sparked debates among 
                technologists, policymakers, and philosophers alike.

                One of the most visible impacts of AI can be seen in healthcare. Machine learning models can now 
                detect anomalies in medical imaging, predict patient outcomes, and even recommend treatment plans. 
                In many cases, AI tools have matched or exceeded the accuracy of human specialists. 
                Yet, this progress also raises important questions: who is responsible when an AI system makes a mistake? 
                Should patients have the right to refuse treatment recommendations generated by an algorithm?

                In business, AI is being used to automate repetitive tasks and analyze customer behavior at scale. 
                Recommendation systems on streaming platforms and online stores are prime examples of this technology 
                in action. These systems continuously learn from user interactions, adapting to provide more personalized 
                experiences. Still, critics argue that such systems often create “echo chambers,” limiting exposure to 
                diverse perspectives or products.

                Education is another domain undergoing transformation. Adaptive learning platforms can tailor lessons to 
                each students progress, providing real-time feedback and helping educators identify areas where students 
                struggle most. But with this customization comes concern over data collection. How much information should 
                educational institutions collect about their students? And who ensures that sensitive data is not misused?

                As AI continues to evolve, regulation becomes increasingly critical. Many governments have proposed or 
                implemented frameworks aimed at ensuring transparency and fairness. The European Union, for instance, 
                has introduced legislation requiring companies to explain the decisions made by their AI systems. 
                This push toward explainable AI reflects a growing global consensus: powerful algorithms must remain accountable.

                Looking ahead, the role of AI in creative industries is set to expand dramatically. From generating 
                artwork and composing music to writing articles and screenplays, AI is blurring the boundaries between 
                human and machine creativity. This evolution presents both an opportunity and a challenge — can AI truly 
                be creative, or is it merely reflecting the creativity of its human programmers?

                In conclusion, while AI offers revolutionary benefits, its responsible development and use will determine 
                whether it serves humanity as a tool for progress or becomes a source of division and control. 
                Balancing innovation with ethics, privacy, and accountability remains the central challenge in the 
                next era of technological advancement.""",
                "success" : True,
                "error" : ""},
            {
                "path": "/test/failed_file.pdf",
                "name": "failed_file.pdf",
                "type": "pdf",
                "content": "",
                "success": False,
                "error": "File parsing failed"
            }
        ]
    }
    
    print("\n" + "=" * 80)
    print("Running pre_process_non_code_files...")
    print("=" * 80)
    
    try:
        results = pre_process_non_code_files(
            sample_parsed_files,
            max_content_length=50000,
            language="english"
        )
        
        print(f"\n✓ Function executed successfully!")
        print("\n" + "=" * 80)
        print("Results:")
        print("=" * 80)
        
        for i, result in enumerate[Dict](results, 1):
            print(f"\n--- File {i}: {result['file_name']} ---")
            print(f"\nSummary ({len(result['summary'])} characters):")
            print(f"  {result['summary']}")
            print(f"\nKey Topics ({len(result['key_topics'])} topics):")
            for j, topic in enumerate(result['key_topics'], 1):
                print(f"  {j}. {topic}")
        
        
    except Exception as e:
        print(f"\n✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()