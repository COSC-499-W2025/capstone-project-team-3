import re
from pathlib import Path
from typing import List, Dict
from collections import Counter
from app.shared.text.parsed_input_text import sample_parsed_files
from app.utils.user_preference_utils import UserPreferenceStore
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import textstat
import spacy

# Send non code parsed content using Sumy LSA Local Pre-processing IF the file exceeds token limit 
#  *This step uses Sumy LSA summarizer (runs locally, no external API calls needed)

def pre_process_non_code_files(parsed_files: Dict, language: str = "english") -> List[Dict]:
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
        # TODO : Intergrate file size checker here
        
        # Skip empty content
        if not content or not content.strip():
            continue
        
        # Dynamically determine the number of summary sentences needed based on content length
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
            
            # Extract file type from file name
            file_type = Path(file_name).suffix.lstrip('.').lower()
            
            # Calculate word count and sentence count
            word_count = len(re.findall(r'\b\w+\b', content))

            # Count sentences based on periods
            sentence_count = len(re.findall(r'\.', content))  # Simple sentence count based on periods

            # Calculate readability score
            readability_score = textstat.flesch_kincaid_grade(content)
            
            # Generate summary using Sumy LSA
            summary = _sumy_lsa_summarize(content, num_sentences=summary_sentences, language=language)
            if not summary:
                summary = ["N/A"]  # Fallback
                raise ValueError("Could not extract summary from content")
                

            # Extract key topics using frequency analysis
            key_topics = _extract_key_topics_(content, num_topics=5)
        
            if not key_topics:
                key_topics = ["N/A"]  # Fallback 
                raise ValueError("Could not extract key topics from content")
                

            llm1_summary = {
                "file_name": file_name,
                "file_path": file_path_str,
                "file_type": file_type,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "readability_score": readability_score,
                "summary": summary.strip(),
                "key_topics": key_topics[:5],  # Limit to 5 main topics per file
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

def _extract_key_topics_(content: str, num_topics: int = 5) -> List[str]:
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

#TODO Implement further metric deduction functions as needed

def get_project_name(llm1_results):
    # Extract Project Name from the file path of the first file
    if llm1_results and "file_path" in llm1_results[0]:
        first_file_path = Path(llm1_results[0]["file_path"])
        return first_file_path.parent.name
    return "Unnamed Project"  # Fallback if project name can't be determined

def get_total_files(llm1_results):
    # Get total number of files processed
    if llm1_results:
        return len(llm1_results)
    return 0

def get_file_names(llm1_results):
    # Get list of all file names
    if llm1_results:
        return [summary["file_name"] for summary in llm1_results]
    return []

def get_readability_metrics(llm1_results):
    # Calculate average readability score across all files
    if llm1_results:
        scores = [summary["readability_score"] for summary in llm1_results if "readability_score" in summary]
        return sum(scores) / len(scores) if scores else None

def get_unique_key_topics(llm1_results):
    # Get unique key topics across all files
    if llm1_results:
        return list(set(topic for summary in llm1_results for topic in summary.get("key_topics", [])))
    return []

def get_file_type_distribution(llm1_results):
    # Get file type distribution across all files
    if llm1_results:
        file_types = [
            summary.get("fileType") or summary.get("file_type")
            for summary in llm1_results
            if "fileType" in summary or "file_type" in summary is not None
        ]
        return dict(Counter(file_types))
    return {}

def get_named_entities(llm1_results):
   # TODO: Use NLP to identify named entities in content for optimized LLM context. [REFACTOR LATER]
    nlp = spacy.load("en_core_web_sm")
    if llm1_results:
        entities = set()
        for summary in llm1_results:
            content = summary.get("summary", "")
            doc = nlp(content)
            entities.update(ent.text for ent in doc.ents)
        return list(entities)
    return []

#Step 3: Aggregate non code summaries into a single analyzable project
def aggregate_non_code_summaries(llm1_results):
    """
    This function aggregates the preprocssed llm1 summary of non-code files into one single project for
    the second LLM to analyze.
    
    Creates aggregated_project_metrics and sends it to the second LLM.
    
    aggregated_project_metrics = {
    "projectName": "Project 1",  # Project-level metadata
    "metadata": {
        "totalFiles": 3,
        "totalWordCount": 15000,
        "totalSentenceCount": 800,
        "averageReadabilityScore": 65.2,
        "uniqueKeyTopics": ["data", "research", "well-being"],
        "mostFrequentWords": ["data", "analysis", "project"],
        "fileTypeDistribution": {"pdf": 2, "txt": 1},
        "namedEntities": ["Team 3", "LLM2", "2025"] #TODO: Use NLP to identify named entities for optimized LLM context
    },
    "files": [  # File-level data
        {
            "file_name": "file1.pdf",
            "file_type": "pdf",
            "word_count": 5000,
            "sentence_count": 200,
            "readability_score": 70.5,
            "summary": "First file summary",
            "keyTopics": ["data", "analysis"]
        },
    """

    
    #This is the project object to be sent to LLM2 (Gemini)
    aggregated_project_metrics = {
        #Project Level data
        "Project_Name": get_project_name(llm1_results), # Project Name extracted from file path
        "totalFiles": get_total_files(llm1_results),
        "fileNames": get_file_names(llm1_results),
        "averageReadabilityScore": get_readability_metrics(llm1_results),
        "uniqueKeyTopics": get_unique_key_topics(llm1_results), # overall unique key topics from all files
        "fileTypeDistribution": get_file_type_distribution(llm1_results),
        "namedEntities": get_named_entities(llm1_results),
        
        #File-level data
        "files" : llm1_results if llm1_results else {}
    }
    return aggregated_project_metrics

#TODO Step 4: Generate prompt for second LLM (Take into account user preferences in PROMPT)
def create_non_code_analysis_prompt(aggregated_project_metrics):
    """
    Create a structured prompt for AI analysis using the aggregated llm1 project summaries.
    Returns formatted prompt string that follows the structure of llm2_metrics.
    """
    user_prefs = UserPreferenceStore.get_latest_preferences_no_email()
    print("DEBUG user_prefs:", user_prefs)

    # Fetch user preferences from DB if available
    if UserPreferenceStore.get_latest_preferences_no_email() is not None:
        user_prefs = UserPreferenceStore.get_latest_preferences_no_email()
        industry = user_prefs.get("industry")
        aspiring_job_title = user_prefs.get("job_title")
        education = user_prefs.get("education")
        
    else:   
        industry = "N/A"  # TODO: Fetch from user profile/preferences
        aspiring_job_title = "N/A"  # TODO: Fetch from user profile/preferences
        education = "N/A"  # TODO: Fetch from user profile/preferences

    # Base prompt structure
    PROMPT = f"""
    You are a precise and detail-oriented Analyst. 
    Your task is to analyze the following project and generate accurate, concise skills and resume bullet points based on the metrics and context information provided. 
    Take into account the industry, aspiring job title, and education if available.   
    Ensure the skills and resume bullet points are relevant to the project content provided.
   
    Project Name: {aggregated_project_metrics["Project_Name"]}
    
    Total Files: {aggregated_project_metrics["totalFiles"]}
    
    File Names: {", ".join(aggregated_project_metrics["fileNames"])}
    
    Average Readability Score: {aggregated_project_metrics["averageReadabilityScore"]}
    
    Unique Key Topics: {", ".join(aggregated_project_metrics["uniqueKeyTopics"])}
    
    File Type Distribution: {aggregated_project_metrics["fileTypeDistribution"]}
    
    Named Entities: {", ".join(aggregated_project_metrics["namedEntities"])}
    
    Industry: {industry}
    
    Aspiring Job Title: {aspiring_job_title}
    
    Education: {education}
    """

    # Add file-level details
    file_details = []
    for file in aggregated_project_metrics.get("files", []):
        file_details.append(f"""
                            
        File Name: {file.get("file_name")}
        
        File Type: {file.get("file_type")}
        
        Word Count: {file.get("word_count")}
        
        Sentence Count: {file.get("sentence_count")}
        
        Readability Score: {file.get("readability_score")}
        
        Summary: {file.get("summary")}
        
        Key Topics: {", ".join(file.get("key_topics", []))}
        
        """)

    # Append file-level details to the prompt
    PROMPT += "\nFile Details:\n" + "\n".join(file_details)

    # Specify the required output format
    PROMPT += """
    Return your analysis in the following format: {
        "skills": [
            "Skill 1",
            "Skill 2", 
            "Skill 3",
            ...
        ],
        "resume_bullets": [
            "Bullet point 1",
            "Bullet point 2",
            "Bullet point 3",
            ...
        ]
    }
    Provide only the JSON object as output without any additional text.
    """
    return PROMPT

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
    #pre_process_non_code_files(parsed_files)

    # 2. Aggregate summaries 
    #aggregate_non_code_summaries(llm1_summary)
    
    # 3. Generate Analysis Prompt
    #create_non_code_analysis_prompt(aggregated_project)
    
    # 4. Call LLM2 for Analysis
    #generate_non_code_insights(PROMPT)

    # 5. Store Data
    #store_non_code_analysis_results(Final_Result)


def run_pipeline():
    """
    Main pipeline to process non-code files, aggregate summaries, and generate project metrics.
    """
    print("\n" + "=" * 80)
    print("Running pre_process_non_code_files...")
    print("=" * 80)

    try:
        # Step 1: Pre-process files
        llm1_results = pre_process_non_code_files(
            sample_parsed_files,
            language="english"
        )
        print("\n✓ Pre-processing completed successfully")

        # Step 2: Aggregate summaries into project metrics
        project_metrics = aggregate_non_code_summaries(llm1_results)
        print_project_metrics(project_metrics)
        print("\n✓ Aggregation completed successfully")
        
        # Step 3 : Generate LLM2 Prompt using aggregated project metrics
        prompt = create_non_code_analysis_prompt(project_metrics)
        print(prompt)
        print("\n✓ Prompt generation completed successfully")

    except Exception as e:
        print(f"\n✗ Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_project_metrics(project_metrics):
    """
    Print the aggregated project metrics in a readable format.
    """
    if not project_metrics:
        print("\n✗ No project metrics to display.")
        return

    print("\n" + "=" * 80)
    print("Project Metrics:")
    print("=" * 80)
    print(f"Project: {project_metrics['Project_Name']}")
    print(f"Total Files: {project_metrics['totalFiles']}")
    print(f"File Names: {project_metrics['fileNames']}")
    print(f"Average Readability Score: {project_metrics['averageReadabilityScore']}")
    print(f"Unique Key Topics: {project_metrics['uniqueKeyTopics']}")
    print(f"File Type Distribution: {project_metrics['fileTypeDistribution']}")
    print(f"Named Entities: {project_metrics['namedEntities']}")
    print(f"Files: {project_metrics['files']}")

# Hardcoded function for CLI run
if __name__ == "__main__":
    run_pipeline()
    
